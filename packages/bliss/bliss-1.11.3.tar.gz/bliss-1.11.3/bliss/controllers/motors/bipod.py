# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Convention for bipod calculations:

    1 - We are using a direct coordiante system (x,y,z) as follow

                    ^
                    | Z axis
                    |
        X axis      |
          <----------
                   /
                  /
                 / Y axis
                /
                v

    2 - The rotation are name rotx, roty, rotz around respectively the
        X, Y and Z axis with counter-clockwize positive value

    3 - all parameters relative to legs are following the same convention:
            - coordinates of "lega" are named: "ax", "ay"
            - coordinates of "legb" are named: "bx", "by"
            - ...

    4 - all parameters are given in meters

    5 - The calculation takes into account the "unit" defined for each
        real or calculated motors.
        if the "unit" field is missing, the universal units are used:
        meters (m) for distance, radians (rad) for angles
"""

import numpy as np
import tabulate

from bliss.common.logtools import log_debug
from bliss.controllers.motor import CalcController
from bliss.physics.units import ur
from bliss.shell.standard import wm
from bliss.config import settings

"""
Table with 2 legs:

    - Definition:

        + the 2 legs are tagged "lega" and "legb"
        + the height of the table is tagged "trans"
        + X-axis is the axis passing thrue lega and legb, positive
          from a to b
        + The rotation is around Y-axis, perpendicular to
          the [lega-legb] axis (X-axis)
        + the rotation is tagged "ry"
        + C is the center of rotation and its height is represented by the
          position of the "dz" axis
        + C is the origin of the X/Y/Z coordinates system
        + "ax" is the coordinate of the leg "lega" in the X/Y/Z coordinates system
        + "bx" is the coordinate of the leg "legb" in the X/Y/Z coordinates system

    - Example of yml file with 2 centers defined:

        * center_id = inside:
            + C is inside the 2 legs
            + "ax" is a negative value in meter
            + "bx" is a positive value in meter

                   Z-axis
                        ^
                        |
                  ______|______________
                 /      |             /
                /       |...ax..>|   /
     X axis    /        |        |  /     X axis
     <--------/-.-------C--------.-/----<------
             /  |<.bx../         |/
            /   |     /          |
           /____|____/__________/|
                |   /            |
                |  v Y-axis      |
                |                |
              legb             lega

        * center_id = outside
            + C is outside the 2 legs
            + "ax" is a positive value in meter
            + "bx" is a positive value in meter

                                        Z-axis
                                          ^
                                          |
                  _____________________   |
                 /                    /   |
                /<.......bx...............|
     X axis    /|                   /     |    X axis
     <--------/-.----------------.-/------C----------
             /  |                |/      /
            /   |                |<.ax../
           /____|_______________/|     /
                |                |    /
                |                |   v Y axis
                |                |
              legb             lega

        + YML file:
            - plugin: emotion
              module: bipod
              class: bipod
              name: btable
              centers:
                - center_id: inside
                  ax: -0.3
                  bx: 0.3
                - center_id: outside
                  ax: 0.3
                  bx: 0.9
              axes:
                - name: $sim_btz1
                  tags: real lega
                - name: $sim_btz2
                  tags: real legb
                - name: sim_btz
                  tags: tz
                  unit: mm
                - name: sim_btr
                  tags: ry
                  unit: deg
"""


class bipod(CalcController):
    """
    Calc controller for 2 legs table.
    """

    def __init__(self, *args, **kwargs):
        CalcController.__init__(self, *args, **kwargs)

        center_params = self.config.get("centers", None)
        if center_params is None:
            raise RuntimeError("No Center defined")

        self._centers = {}
        for center_param in center_params:
            center_id = center_param.get("center_id", None)
            default_center = center_id
            if center_id is None:
                raise RuntimeError("No center_id defined")
            self._centers[center_id] = {}
            for key in ["ax", "bx"]:
                self._centers[center_id][key] = center_param.get(key, 0)

            ax = self._centers[center_id]["ax"]
            bx = self._centers[center_id]["bx"]
            log_debug(self, f"center_id: {center_id}")
            log_debug(self, f"    ax = {ax}")
            log_debug(self, f"    bx = {bx}")

        self._selected_center = settings.SimpleSetting(
            f"tripod_{self.name}_selected_center",
            default_value=default_center,
        )

    def initialize(self):
        CalcController.initialize(self)

        # get all motor units
        self.lega_unit = self._tagged["lega"][0].unit
        self.legb_unit = self._tagged["legb"][0].unit
        self.tz_unit = self._tagged["tz"][0].unit
        self.ry_unit = self._tagged["ry"][0].unit

    def __info__(self):
        """
        Return info string for inline doc.
        """
        mystr = "Type           : bipod\n\n"
        mystr += f"Selected center: {self.center}\n"
        mystr += f"    ax = {self.ax}\n"
        mystr += f"    bx = {self.bx}\n\n"
        title = []
        user = []
        for axis in self.pseudos:
            title.append(f"{axis.name}[{axis.unit}]")
            user.append(f"{axis.position:.4f}")
        mystr += tabulate.tabulate([title, user], tablefmt="plain")
        mystr += "\n\n"
        title = []
        user = []
        for axis in self.reals:
            title.append(f"{axis.name}[{axis.unit}]")
            user.append(f"{axis.position:.4f}")
        mystr += tabulate.tabulate([title, user], tablefmt="plain")
        return mystr

    def wa(self):
        mot_list = self.pseudos + self.reals
        wm(*mot_list)

    @property
    def center(self):
        return self._selected_center.get()

    @center.setter
    def center(self, center_id):
        if center_id in self._centers.keys():
            self._selected_center.set(center_id)
            self.sync_hard()

    @property
    def ax(self):
        return self._centers[self.center]["ax"]

    @property
    def bx(self):
        return self._centers[self.center]["bx"]

    def calc_from_real(self, real_dict):

        log_debug(self, "calc_from_real()")

        lega = (real_dict["lega"] * ur.parse_units(self.lega_unit)).to("m").magnitude
        legb = (real_dict["legb"] * ur.parse_units(self.legb_unit)).to("m").magnitude

        if not isinstance(lega, np.ndarray):
            lega = np.array([lega], dtype=float)
            legb = np.array([legb], dtype=float)

        ry = np.arctan((lega - legb) / (self.bx - self.ax))
        tz = lega + self.ax * np.tan(ry)

        ry = (ry * ur.rad).to(self.ry_unit).magnitude
        tz = (tz * ur.m).to(self.tz_unit).magnitude

        if len(lega) == 1:
            return {"tz": tz[0], "ry": ry[0]}
        return {"tz": tz, "ry": ry}

    def calc_to_real(self, calc_dict):

        log_debug(self, "calc_to_real()")

        tz = (calc_dict["tz"] * ur.parse_units(self.tz_unit)).to("m").magnitude
        ry = (calc_dict["ry"] * ur.parse_units(self.ry_unit)).to("rad").magnitude

        if not isinstance(tz, np.ndarray):
            tz = np.array([tz], dtype=float)
            ry = np.array([ry], dtype=float)

        lega = tz - self.ax * np.tan(ry)
        legb = tz - self.bx * np.tan(ry)

        lega = (lega * ur.m).to(self.lega_unit).magnitude
        legb = (legb * ur.m).to(self.legb_unit).magnitude

        if len(tz) == 1:
            return {"lega": lega[0], "legb": legb[0]}
        return {"lega": lega, "legb": legb}
