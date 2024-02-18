# -*- coding: utf-8 -*-
#
# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import tabulate
import enum


class RegulState(enum.IntEnum):
    Off = 0
    On = 1


class RegulError(enum.IntEnum):
    NoError = 0
    MinInput = 1
    MaxInput = 2
    MinOutput = 3
    MaxOutput = 4
    ExtError = 5


"""
SPEEDGOAT REGULATOR
"""


class SpeedgoatHdwRegulController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._reguls = None
        self._load()

    def __info__(self):
        if self._reguls is None:
            return "    No Regulator in the model"
        lines = [["    ", "Name", "Unique Name"]]
        for regul in self._reguls.values():
            lines.append(["    ", regul.name, regul._unique_name])
        mystr = "\n" + tabulate.tabulate(lines, tablefmt="plain", stralign="right")
        return mystr

    def _load(self, force=False):
        if self._reguls is None or force:
            reguls = self._speedgoat._get_all_objects_from_key("bliss_regulator")
            if len(reguls) > 0:
                self._reguls = {}
                for regul in reguls:
                    sp_regul = SpeedgoatHdwRegul(self._speedgoat, regul)
                    setattr(self, sp_regul.name, sp_regul)
                    self._reguls[sp_regul.name] = sp_regul
        return self._reguls


class SpeedgoatHdwRegul:
    def __init__(self, speedgoat, unique_name):
        self._speedgoat = speedgoat
        self._unique_name = unique_name
        self.name = self._speedgoat.parameter.get(
            f"{self._unique_name}/bliss_regulator/String"
        )

    def __info__(self):
        lines = []
        lines.append(["Name", self.name])
        lines.append(["Unique Name", self._unique_name])
        lines.append(["", ""])
        lines.append(["State", self.state.name])
        lines.append(["Error", self.error.name])
        lines.append(["Wanted", self.wanted])
        lines.append(["Fault output", list(self.fault_output)])
        lines.append(["", ""])
        lines.append(["Input", self.input])
        lines.append(["Output", self.output])
        lines.append(["", ""])
        lines.append(["Max_input_neg", self.max_input_neg])
        lines.append(["Max_input_pos", self.max_input_pos])
        lines.append(["Max_output_neg", self.max_output_neg])
        lines.append(["Max_output_pos", self.max_output_pos])
        mystr = "\n" + tabulate.tabulate(lines, tablefmt="plain", stralign="right")
        return mystr

    def _tree(self):
        self._speedgoat.parameter._load()["param_tree"].subtree(
            self._unique_name
        ).show()

    @property
    def max_input_neg(self):
        return self._speedgoat.parameter.get(f"{self._unique_name}/max_input_neg")

    @max_input_neg.setter
    def max_input_neg(self, value):
        if value < self.max_input_pos:
            self._speedgoat.parameter.set(f"{self._unique_name}/max_input_neg", value)
        else:
            raise ValueError(f"max_input_neg {value} must be < {self.max_input_pos}")

    @property
    def max_input_pos(self):
        return self._speedgoat.parameter.get(f"{self._unique_name}/max_input_pos")

    @max_input_pos.setter
    def max_input_pos(self, value):
        if value > self.max_input_neg:
            self._speedgoat.parameter.set(f"{self._unique_name}/max_input_pos", value)
        else:
            raise ValueError(f"max_input_pos {value} must be > {self.max_input_neg}")

    @property
    def max_output_neg(self):
        return self._speedgoat.parameter.get(f"{self._unique_name}/max_output_neg")

    @max_output_neg.setter
    def max_output_neg(self, value):
        if value < self.max_output_pos:
            self._speedgoat.parameter.set(f"{self._unique_name}/max_output_neg", value)
        else:
            raise ValueError(f"max_output_neg {value} must be < {self.max_output_pos}")

    @property
    def max_output_pos(self):
        return self._speedgoat.parameter.get(f"{self._unique_name}/max_output_pos")

    @max_output_pos.setter
    def max_output_pos(self, value):
        if value > self.max_output_neg:
            self._speedgoat.parameter.set(f"{self._unique_name}/max_output_pos", value)
        else:
            raise ValueError(f"max_output_pos {value} must be > {self.max_output_neg}")

    @property
    def wanted(self):
        return bool(int(self._speedgoat.parameter.get(f"{self._unique_name}/wanted")))

    def on(self):
        self.reset_error()
        self._speedgoat.parameter.set(f"{self._unique_name}/wanted", 1)

    def off(self):
        self._speedgoat.parameter.set(f"{self._unique_name}/wanted", 0)

    def reset_error(self):
        reset_error = int(
            self._speedgoat.parameter.get(f"{self._unique_name}/reset_error/Bias")
        )
        self._speedgoat.parameter.set(
            f"{self._unique_name}/reset_error/Bias", reset_error + 1
        )

    @property
    def fault_output(self):
        return self._speedgoat.parameter.get(f"{self._unique_name}/fault_output")

    @fault_output.setter
    def fault_output(self, value):
        nb = len(self.fault_output)
        if nb != len(value):
            raise ValueError(f"Value must be a list of {nb} elements")
        self._speedgoat.parameter.set(f"{self._unique_name}/fault_output", value)

    @property
    def error(self):
        # 0:no_error 1:min_input_reached 2:max_input_reached 3:min_output_reached 4:max_output_reached 5:ext_error
        return RegulError(int(self._speedgoat.signal.get(f"{self._unique_name}/error")))

    @property
    def state(self):
        # 0:off 1:on
        return RegulState(
            int(self._speedgoat.signal.get(f"{self._unique_name}/status"))
        )

    @property
    def input(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/input")

    @property
    def output(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/output")
