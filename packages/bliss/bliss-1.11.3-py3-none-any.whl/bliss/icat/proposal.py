# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import datetime
from typing import Iterable, Tuple, List, Union
import numpy
from blissdata.data.node import DataNode
from bliss.icat.policy import DataPolicyObject
from bliss.icat.client import DatasetId


class Proposal(DataPolicyObject):
    _NODE_TYPE = "proposal"

    @property
    def dataset_collection_nodes(self):
        yield from self.child_nodes

    @property
    def has_dataset_collections(self):
        try:
            next(self.dataset_collection_nodes)
        except StopIteration:
            return False
        else:
            return True

    @property
    def sample_nodes(self):
        yield from self.child_nodes

    @property
    def has_samples(self):
        return self.has_dataset_collections

    @property
    def unconfirmed_dataset_ids(self) -> List[DatasetId]:
        return [
            DatasetId(name=dataset.name, path=dataset.path)
            for dataset in self._iter_unconfirmed_datasets()
        ]

    def get_dataset_node(self, dataset_name_or_id: Union[DatasetId, str]) -> DataNode:
        for collection in self.child_nodes:
            for dataset in collection.children():
                if isinstance(dataset_name_or_id, str):
                    found = dataset_name_or_id == dataset.name
                else:
                    found = (
                        DatasetId(name=dataset.name, path=dataset.path)
                        == dataset_name_or_id
                    )
                if found:
                    return dataset

    def _iter_unconfirmed_datasets(self) -> Iterable[DataNode]:
        """An "unconfirmed" dataset is marked in Redis as "closed" and "unregistered"."""
        for collection in self.child_nodes:
            for dataset in collection.children():
                if not dataset.is_registered and dataset.is_closed:
                    yield dataset

    def unconfirmed_dataset_info_string(self) -> str:
        rows = list(self._iter_unconfirmed_dataset_info())
        if not rows:
            return ""
        lengths = numpy.array([[len(s) for s in row] for row in rows])
        fmt = "   ".join(["{{:<{}}}".format(n) for n in lengths.max(axis=0)])
        infostr = "Unconfirmed datasets:\n "
        infostr += fmt.format("Name", "Time since end", "Path")
        infostr += "\n "
        infostr += "\n ".join([fmt.format(*row) for row in rows])
        return infostr

    def _iter_unconfirmed_dataset_info(self) -> Iterable[Tuple[str, str, str]]:
        now = datetime.datetime.now()
        for dataset in self._iter_unconfirmed_datasets():
            end_date = dataset.end_date
            if end_date is None:
                time_since_end = "NaN"
            else:
                time_since_end = str(now - end_date)
            yield dataset.name, time_since_end, dataset.path

    @property
    def _data_db_names_depth(self) -> int:
        """The Redis node depth at which the data nodes exist"""
        return 3

    @classmethod
    def child_type(cls):
        from bliss.icat.dataset import DatasetCollection

        return DatasetCollection
