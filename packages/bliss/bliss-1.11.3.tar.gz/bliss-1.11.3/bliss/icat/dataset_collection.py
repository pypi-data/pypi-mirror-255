# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.


from bliss.icat.policy import DataPolicyObject
from bliss.icat.proposal import Proposal
from bliss.common.utils import autocomplete_property


class DatasetCollection(DataPolicyObject):
    _NODE_TYPE = "dataset_collection"

    def __init__(self, node):
        super().__init__(node)
        self._proposal = None
        self._expected_field = {"Sample_name", "Sample_description"}

    @property
    def proposal(self):
        if self._proposal is None:
            if self._node.parent is not None:
                self._proposal = Proposal(self._node.parent)
        return self._proposal

    @property
    def parent(self):
        return self.proposal

    @property
    def dataset_nodes(self):
        yield from self.child_nodes

    @property
    def has_datasets(self):
        try:
            next(self.dataset_nodes)
        except StopIteration:
            return False
        else:
            return True

    @autocomplete_property
    def sample_name(self):
        return self.get_metadata_field("Sample_name")

    @sample_name.setter
    def sample_name(self, value):
        self["Sample_name"] = value

    @autocomplete_property
    def sample_description(self):
        # TODO: use Dataset_description when it gets introduced
        return self.get_metadata_field("Sample_description")

    @sample_description.setter
    def sample_description(self, value):
        # TODO: use Dataset_description when it gets introduced
        self["Sample_description"] = value

    @property
    def _data_db_names_depth(self) -> int:
        """The Redis node depth at which the data nodes exist"""
        return 2

    @classmethod
    def child_type(cls):
        from bliss.icat.dataset import Dataset

        return Dataset
