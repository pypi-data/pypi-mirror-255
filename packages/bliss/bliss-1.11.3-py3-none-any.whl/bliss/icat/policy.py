# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import re
from typing import Iterable, Set, Tuple

from pyicat_plus.metadata.definitions import load_icat_fields

from bliss.common.logtools import log_debug, log_warning
from bliss.common.utils import autocomplete_property
from bliss.common.namespace_wrapper import NamespaceWrapper
from blissdata.data.expiration import set_expiration_time
from blissdata.data.expiration import remove_expiration_time
from blissdata.settings import scan as scan_redis
from bliss import current_session
from bliss.icat.metadata import ICATmetadata


class DataPolicyObject:
    """A data policy object with a Redis representation that
    allows for storing ICAT metadata fields
    """

    _REQUIRED_INFO = {"__name__", "__path__"}
    _NODE_TYPE = NotImplemented

    def __init__(self, node):
        """
        :param DataNodeContainer node:
        """
        self._node = node
        node_type = node.type
        if node_type != self._NODE_TYPE:
            raise RuntimeError(
                f"Node type must be '{self._NODE_TYPE}' instead of '{node_type}'"
            )
        existing = set(node.info.keys())
        undefined = self._REQUIRED_INFO - existing
        if undefined:
            raise RuntimeError(f"Missing node info: {undefined}")
        self.__icat_fields = None
        self.__metadata_namespace = None
        self.__definitions = None
        self._expected_field = set()

    def __str__(self):
        return self.name

    def __setitem__(self, key, value):
        """Set metadata field in Redis"""
        self.write_metadata_field(key, value)

    def __getitem__(self, key):
        """Get metadata field from Redis"""
        return self.read_metadata_field(key)

    def __contains__(self, key):
        """Check metadata field in Redis"""
        return self.has_metadata_field(key)

    @property
    def name(self):
        return self._node.info["__name__"]

    @property
    def path(self):
        return self._node.info["__path__"]

    @property
    def node(self):
        return self._node

    @property
    def child_nodes(self):
        yield from self._node.children()

    @classmethod
    def child_type(cls):
        return None

    @property
    def children(self):
        cls = self.child_type()
        if cls is not None:
            for node in self._node.children():
                yield cls(node)

    @property
    def is_frozen(self):
        """Forzen means it does take metadata fields from its parent"""
        return self._node.info.get("__frozen__")

    def _log_debug(self, msg):
        log_debug(self, f"{self._NODE_TYPE}({self}): {msg}")

    def _log_warning(self, msg):
        log_warning(self, f"{self._NODE_TYPE}({self}): {msg}")

    @property
    def parent(self):
        return None

    def get_current_icat_metadata(self, pattern=None):
        """Get all metadata key-value pairs from Redis (self and parents)"""
        if not self.is_frozen and self.parent:
            metadata = self.parent.get_current_icat_metadata(pattern=pattern)
            metadata.update(self._node.get_metadata(pattern=pattern))
        else:
            metadata = self._node.get_metadata(pattern=pattern)
        return metadata

    def get_current_icat_metadata_fields(self, pattern=None):
        """Get all metadata field names from Redis (self and parents)."""
        metadata_fields = self._node.get_metadata_fields(pattern=pattern)
        if not self.is_frozen and self.parent:
            metadata_fields |= self.parent.get_current_icat_metadata_fields(
                pattern=pattern
            )
        return metadata_fields

    def freeze_inherited_icat_metadata(self):
        """After this, changes in the parent metadata no longer affect
        the current metadata.
        """
        if self.is_frozen or not self.parent:
            return
        self_fields = self._node.get_metadata_fields()
        parent_fields = self.parent.get_current_icat_metadata_fields()
        for key in parent_fields - self_fields:
            value = self.parent.read_metadata_field(key)
            self.write_metadata_field(key, value)
        self._node.info["__frozen__"] = True

    def unfreeze_inherited_icat_metadata(self):
        """After this, the parent metadata affect the current metadata."""
        self._node.info["__frozen__"] = False

    def has_metadata_field(self, key):
        """Check metadata field exists in Redis (self and parents)."""
        return key in self.get_current_icat_metadata_fields()

    def read_metadata_field(self, key):
        """Get the value of one metadata field from Redis (self and parents).
        Raises `KeyError` when field is missing.
        """
        try:
            return self._node.info[key]
        except KeyError:
            if self.parent:
                return self.parent.read_metadata_field(key)
            else:
                raise

    def get_metadata_field(self, key, default=None):
        """Get the value of one metadata field from Redis (self and parents).
        Returns `default` when field is missing.
        """
        try:
            return self.read_metadata_field(key)
        except KeyError:
            return default

    def write_metadata_field(self, key, value):
        """Store metadata key-value pair in Redis. Does not affect the parent.
        Remove key when the value is `None`.
        Raises `KeyError` when the key is not valid.
        Raises `ValueError` when the value is not a string.
        """
        if value is None:
            self.remove_metadata_field(key)
            return
        if not self.validate_field_name(key):
            raise KeyError(f"{repr(key)} is not a valid ICAT field")
        self._node.info[key] = value

    def remove_metadata_field(self, key):
        """Remove a metadata field from Redis if it exists.
        Does not affect the parents.
        """
        self._node.info.pop(key, None)

    def remove_all_metadata_fields(self):
        """Remove a metadata field from Redis if it exists.
        Does not affect the parents.
        """
        for key in self.get_current_icat_metadata_fields():
            self.remove_metadata_field(key)

    @property
    def _icat_fields(self) -> ICATmetadata:
        if self.__icat_fields is None:
            try:
                self.__icat_fields = current_session.icat_metadata._icat_fields
            except AttributeError:
                self.__icat_fields = load_icat_fields()
        return self.__icat_fields

    @autocomplete_property
    def definitions(self) -> NamespaceWrapper:
        if self.__definitions is None:
            self.__definitions = self._icat_fields.namespace()
        return self.__definitions

    @autocomplete_property
    def metadata(self) -> NamespaceWrapper:
        if self.__metadata_namespace is None:
            self.__metadata_namespace = self._icat_fields.namespace(
                getter=self.get_metadata_field, setter=self.write_metadata_field
            )
        return self.__metadata_namespace

    def validate_field_name(self, field_name: str) -> bool:
        return self._icat_fields.valid_field_name(field_name)

    @autocomplete_property
    def all(self) -> NamespaceWrapper:
        """namespace to access all possible keys"""
        names = [field.field_name for field in self._icat_fields.iter_fields()]
        return NamespaceWrapper(
            names, self.get_metadata_field, self.write_metadata_field
        )

    @property
    def expected_fields(self):
        """all required metadata fields"""
        if self.parent:
            return self._expected_field | self.parent.expected_fields
        else:
            return self._expected_field

    @autocomplete_property
    def expected(self):
        """namespace to read/write expected metadata fields"""
        return NamespaceWrapper(
            self.expected_fields, self.get_metadata_field, self.write_metadata_field
        )

    @property
    def existing_fields(self):
        """all existing metadata fields"""
        return self.get_current_icat_metadata_fields()

    @autocomplete_property
    def existing(self) -> NamespaceWrapper:
        """namespace to read/write existing metadata fields"""
        return NamespaceWrapper(
            self.existing_fields, self.get_metadata_field, self.write_metadata_field
        )

    @property
    def missing_fields(self):
        """returns a list of required metadata fields that are not yet filled"""
        return self.expected_fields.difference(self.existing_fields)

    @autocomplete_property
    def missing(self):
        """namespace to read/write mising metadata fields"""
        return NamespaceWrapper(
            self.missing_fields, self.get_metadata_field, self.write_metadata_field
        )

    def check_metadata_consistency(self):
        """returns True when all required metadata fields are filled"""
        mtf = self.missing_fields
        if mtf:
            self._log_warning(
                f"The following metadata fields are expected by a given technique but not provided: {mtf}"
            )
        return not mtf

    @property
    def metadata_is_complete(self):
        return not self.missing_fields

    @property
    def _data_db_names_depth(self):
        """The Redis node depth at which the data nodes exist"""
        raise NotImplementedError

    def _get_db_names(self, include_parents=True) -> Tuple[set, set]:
        """Returns the Redis keys of the data policy nodes and the data nodes.
        Parent data policy nodes are optional.
        """
        policy_db_names = set(self.node.get_db_names(include_parents=include_parents))
        prefix = self.node.db_name
        child_db_names = set(scan_redis(prefix + ":*", connection=self.node.connection))
        keep_level = ":".join(["[^:]+"] * self._data_db_names_depth)
        data_pattern = re.compile(f"^{re.escape(prefix)}:{keep_level}:.+$")
        data_db_names = {
            db_name for db_name in child_db_names if data_pattern.match(db_name)
        }
        policy_db_names |= child_db_names - data_db_names
        return policy_db_names, data_db_names

    def set_expiration_time(self, include_parents=True):
        """Includes node and children nodes. Parent nodes are optional."""
        policy_db_names, data_db_names = self._get_db_names(
            include_parents=include_parents
        )
        set_expiration_time(data_db_names, data=True)
        set_expiration_time(policy_db_names, data=False)

    def remove_expiration_time(self, include_parents=True):
        """Does not remove the expiration time from the data nodes."""
        policy_db_names, _ = self._get_db_names(include_parents=include_parents)
        remove_expiration_time(policy_db_names)

    def redo_expiration_time(self):
        """Apply the expiration time as determined by the state of the nodes."""
        self.remove_expiration_time()
        for child in self.children:
            child.redo_expiration_time()

    @autocomplete_property
    def techniques(self) -> Set[str]:
        definition = self.get_metadata_field("definition")
        if definition:
            return set(definition.split(" ")) - {"UNKNOWN"}
        else:
            return set()

    def add_techniques(self, *techniques: Iterable[str]):
        existing = self.techniques
        existing.update(s.upper() for s in techniques)
        definition = " ".join(sorted(existing))
        self.write_metadata_field("definition", definition)

    def remove_techniques(self, *techniques: Iterable[str]) -> None:
        remove = set(s.upper() for s in techniques)
        techniques = self.techniques - remove
        definition = " ".join(sorted(techniques))
        self.write_metadata_field("definition", definition)
