# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
This file groups all protocols managed by bliss
"""

import weakref

from abc import ABC
from types import SimpleNamespace
from typing import List, Mapping, Optional
from typing_extensions import Protocol, runtime_checkable


class IterableNamespace(SimpleNamespace):
    """Access to this namespace is compatible with named_tuple"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getitem__(self, key):
        """works for both keys of dict or integer values of key"""
        try:
            return self.__dict__.__getitem__(key)
        except KeyError:
            return list(self.__dict__.values())[key]

    @property
    def _fields(self):
        """as for named tuple"""
        return self.__dict__.keys()

    def __add__(self, other):
        if isinstance(other, IterableNamespace):
            return IterableNamespace(**{**self.__dict__, **other.__dict__})
        elif isinstance(other, Mapping):
            return IterableNamespace(**{**self.__dict__, **other})
        else:
            raise TypeError

    def __info__(self):
        names = "".join(["." + x + "\n" for x in self.__dict__.keys()])
        return "Namespace containing:\n" + names

    def __len__(self):
        return len(self.__dict__)


def counter_namespace(counters):
    if isinstance(counters, dict):
        dct = counters
    elif isinstance(counters, IterableNamespace):
        return counters
    else:
        dct = {counter.name: counter for counter in counters}
    return IterableNamespace(**dct)
    # return namedtuple("namespace", dct)(**dct)


class CounterContainer(ABC):
    """
    Device that contains counters.
    """

    @property
    def counters(self) -> IterableNamespace:
        """
        Return a **counter_namespace** which hold a list of counters
        attached to this device.
        """
        raise NotImplementedError


class Scannable(ABC):
    """
    Any device that has this interface can be used
    in a step by step scan.
    """

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def position(self) -> float:
        """
        Return the current position
        """
        raise NotImplementedError

    @property
    def state(self):
        """
        Return the current state.
        """
        raise NotImplementedError

    def move(self, target_position):
        """
        This should move to target_position
        """
        raise NotImplementedError


class HasMetadataForDataset(ABC):
    """
    Any controller which provides metadata intended to be saved
    during a dataset life cycle.

    The `dataset_metadata` is called by the Bliss session's icat_metadata
    object when the session has such a mapping configured.
    """

    _DISABLED_DATASET_METADATA_CONTROLLERS = weakref.WeakSet()

    def disable_dataset_metadata(self):
        HasMetadataForDataset._DISABLED_DATASET_METADATA_CONTROLLERS.add(self)

    @property
    def dataset_metadata_enabled(self):
        return self not in HasMetadataForDataset._DISABLED_DATASET_METADATA_CONTROLLERS

    def enable_dataset_metadata(self):
        try:
            HasMetadataForDataset._DISABLED_DATASET_METADATA_CONTROLLERS.remove(self)
        except KeyError:
            pass

    def dataset_metadata(self) -> Optional[dict]:
        """
        Returning an empty dictionary means the controller has metadata
        but no values. `None` means the controller has no metadata.
        """
        raise NotImplementedError

    def dataset_metadata_groups(self) -> List[str]:
        """
        When this list is not empty, metadata of this object will be discovered automatically.
        """
        return list()


class HasMetadataForScan(ABC):
    """
    Any controller which provides metadata intended to be saved
    during a scan life cycle.
    """

    _DISABLED_SCAN_METADATA_CONTROLLERS = weakref.WeakSet()

    def disable_scan_metadata(self):
        HasMetadataForScan._DISABLED_SCAN_METADATA_CONTROLLERS.add(self)

    @property
    def scan_metadata_enabled(self):
        return self not in HasMetadataForScan._DISABLED_SCAN_METADATA_CONTROLLERS

    def enable_scan_metadata(self):
        try:
            HasMetadataForScan._DISABLED_SCAN_METADATA_CONTROLLERS.remove(self)
        except KeyError:
            pass

    def scan_metadata(self) -> Optional[dict]:
        """
        Returning an empty dictionary means the controller has metadata
        but no values. `None` means the controller has no metadata.
        """
        raise NotImplementedError

    @property
    def scan_metadata_name(self) -> Optional[str]:
        """
        Default implementation returns self.name, can be overwritten in derived classes
        Returns None when there is no name
        """
        try:
            return self.name
        except AttributeError:
            return None

    def _generate_metadata(self, scan):
        """
        Method used by `ScanMeta` to populate the scan metadata with metadata related to this controller.
        """
        from bliss.common.logtools import user_error

        metadata_name = self.scan_metadata_name
        if not metadata_name:
            user_error(f"{repr(self)} needs a name to publish scan metadata")
            return {}
        try:
            return {metadata_name: self.scan_metadata()}
        except Exception:
            try:
                name = self.name
            except AttributeError:
                name = repr(self)
            user_error(
                f"error in generating metadata from controller {repr(name)}",
                exc_info=True,
            )
            return {}


class HasMetadataForScanExclusive(HasMetadataForScan):
    """
    Any controller which provides metadata intended to be saved
    during a scan life cycle when used in the acquisition chain.
    """

    pass


class ErrorReportInterface(ABC):
    @property
    def is_loading_config(self):
        raise NotImplementedError

    @is_loading_config.setter
    def is_loading_config(self, val):
        raise NotImplementedError

    def display_exception(self, exc_type, exc_value, tb):
        raise NotImplementedError


@runtime_checkable
class HasInfo(Protocol):
    def __info__(self):
        ...
