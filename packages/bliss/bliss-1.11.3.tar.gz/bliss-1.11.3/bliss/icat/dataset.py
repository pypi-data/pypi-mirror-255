# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.


import os
import datetime
from bliss import current_session
from bliss.common.utils import autocomplete_property
from bliss.icat.policy import DataPolicyObject
from bliss.icat.dataset_collection import DatasetCollection


class Dataset(DataPolicyObject):
    """A dataset can be

     * closed: metadata is gathered and frozen which means metadata cannot be
               changed or added and parent metadata is not inherited
     * registered: metadata is registered with ICAT

    A registered dataset is always closed but a closed dataset is not necessarily registered.
    """

    _REQUIRED_INFO = DataPolicyObject._REQUIRED_INFO | {"__closed__", "__registered__"}
    _NODE_TYPE = "dataset"

    def __init__(self, node):
        super().__init__(node)
        self._collection = None

    @property
    def expected_fields(self):
        """all fields required by this dataset"""
        all_fields = super().expected_fields
        # All technique related fields are expected:
        techniques = self.techniques
        if techniques:
            for group in self._icat_fields.iter_groups_with_type("technique"):
                if group.info.name in techniques:
                    all_fields.update(field.field_name for field in group.iter_fields())
        return all_fields

    def gather_metadata(self, on_exists=None):
        """Initialize the dataset node info.

        When metadata already exists in Redis:
            on_exists="skip": do nothing
            on_exists="overwrite": overwrite in Redis
            else: raise RuntimeError
        """
        if self.is_closed:
            raise RuntimeError("The dataset is already closed")

        if self.metadata_gathering_done:
            if on_exists == "skip":
                return
            elif on_exists == "overwrite":
                pass
            else:
                raise RuntimeError("Metadata gathering already done")

        # Gather metadata
        if current_session.icat_metadata:
            infodict = current_session.icat_metadata.get_metadata(
                techniques=self.techniques
            )
        else:
            infodict = dict()

        # Add other info keys (not metadata)
        infodict["__metadata_gathered__"] = True

        # Update the node's info
        self._node.info.update(infodict)

    @property
    def metadata_gathering_done(self):
        return self._node.info.get("__metadata_gathered__", False)

    def finalize_metadata(self):
        if not self.has_metadata_field("definition"):
            self.write_metadata_field("definition", "UNKNOWN")
        self.write_metadata_field("endDate", datetime.datetime.now())

    def close(self, icat_client, raise_on_error=True):
        """Close the dataset in Redis and send to ICAT.
        The dataset will not be closed when it has no data on disk.
        """
        if self.is_registered:
            msg = f"dataset {self.name} is already registered with ICAT"
            if raise_on_error:
                raise RuntimeError(msg)
            else:
                self._log_debug(msg)
                return
        if self.is_closed:
            msg = f"dataset {self.name} is already closed"
            if raise_on_error:
                raise RuntimeError(msg)
            else:
                self._log_debug(msg)
                return
        if not self.has_data:
            self._log_debug(f"dataset {self.name} is not closed because no data")
            return
        self._raw_close()
        self.register_with_icat(icat_client, raise_on_error=raise_on_error)
        if icat_client.expire_datasets_on_close:
            self.set_expiration_time(include_parents=False)

    def _raw_close(self):
        self.finalize_metadata()
        self.freeze_inherited_icat_metadata()
        self._node.info["__closed__"] = True
        self._log_debug(f"dataset {self.name} is closed")

    def confirm_registration(self, raise_on_error=True):
        """Called when it has been confirmed that the dataset was
        registered in ICAT.
        """
        if not self.is_closed:
            msg = f"dataset {self.name} is not closed"
            if raise_on_error:
                raise RuntimeError(msg)
            else:
                self._log_debug(msg)
                return
        if not self.is_registered:
            self.set_expiration_time(include_parents=False)
            self._node.info["__registered__"] = True
            self._log_debug("confirm dataset registration")

    def redo_expiration_time(self):
        if self.is_registered:
            self.set_expiration_time(include_parents=False)
        else:
            self.remove_expiration_time(include_parents=False)

    def register_with_icat(self, icat_client, raise_on_error=True):
        """Only registered with ICAT when the path exists. This call is
        asynchronous which means we won't have confirmation of success
        or failure.
        """
        if self.is_registered:
            msg = f"dataset {self.name} is already registered with ICAT"
            if raise_on_error:
                raise RuntimeError(msg)
            else:
                self._log_debug(msg)
                return
        if not self.is_closed:
            msg = f"dataset {self.name} is not closed"
            if raise_on_error:
                raise RuntimeError(msg)
            else:
                self._log_debug(msg)
                return
        if not self.has_data:
            self._log_debug(
                f"dataset {self.name} is not registered because it has no data"
            )
            return
        self._log_debug(f"register dataset {self.name} with ICAT")
        icat_client.store_dataset(
            proposal=self.proposal.name,
            dataset=self.name,
            path=self.path,
            metadata=self.get_current_icat_metadata(),
        )

    def save_for_icat(self, icat_client, store_filename: str):
        """Save the dataset to be send to ICAT later"""
        if not self.has_data:
            self._log_debug(f"dataset {self.name} is not saved because it has no data")
            return
        self._log_debug(f"save dataset {self.name} for ICAT in {store_filename}")
        icat_client.store_dataset(
            proposal=self.proposal.name,
            dataset=self.name,
            path=self.path,
            metadata=self.get_current_icat_metadata(),
            store_filename=store_filename,
        )

    @autocomplete_property
    def collection(self):
        if self._collection is None:
            if self._node.parent is not None:
                self._collection = DatasetCollection(self._node.parent)
        return self._collection

    @autocomplete_property
    def proposal(self):
        if self.collection is None:
            return None
        else:
            return self.collection.proposal

    @property
    def parent(self):
        return self.collection

    @property
    def scan_nodes(self):
        yield from self.child_nodes

    @property
    def has_scans(self):
        try:
            next(self.scan_nodes)
        except StopIteration:
            return False
        else:
            return True

    @property
    def has_data(self):
        return os.path.exists(self.path)

    @property
    def is_closed(self):
        return self._node.is_closed

    @property
    def is_registered(self):
        return self._node.is_registered

    @autocomplete_property
    def description(self):
        # TODO: use Dataset_description when it gets introduced
        return self.get_metadata_field("Sample_description")

    @description.setter
    def description(self, value):
        # TODO: use Dataset_description when it gets introduced
        if value is not None:
            # TODO: remove this block when Dataset_description gets introduced
            sample_description = self.sample_description
            if sample_description:
                value = f"{sample_description} ({value})"
        self["Sample_description"] = value

    @autocomplete_property
    def sample_description(self):
        # TODO: use Dataset_description when it gets introduced
        return self.collection.sample_description

    @sample_description.setter
    def sample_description(self, value):
        # TODO: use Dataset_description when it gets introduced
        self.collection.sample_description = value

    @autocomplete_property
    def sample_name(self):
        return self.get_metadata_field("Sample_name")

    @sample_name.setter
    def sample_name(self, value):
        self["Sample_name"] = value

    @property
    def _data_db_names_depth(self) -> int:
        """The Redis node depth at which the data nodes exist"""
        return 1
