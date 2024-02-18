# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from .diff_base import Diffractometer


class DiffZAXIS(Diffractometer):

    PSEUDOS_FMT = """\
H K L = {pos[hkl_h]:f} {pos[hkl_k]:f} {pos[hkl_l]:f}
TWO THETA = {pos[tth2_tth]:f}
Alpha = {pos[incidence_incidence]:.5g}  Beta = {pos[emergence_emergence]:.5g}
"""

    def show(self):

        print(("\nZAXIS Geometry, HKL mode : {0}".format(self.hklmode)))
        if len(self.frozen_angles_names):
            if len(self.frozen_angles):
                for name, value in self.frozen_angles.items():
                    print("Frozen {0:s} = {1:.4f}".format(name, value))
            else:
                print("No angles frozen yet.")
        if self.hklmode == "psi_constant":
            print("Constant psi = {0:.4f}".format(self.psi_constant))

        if self.sample.get_n_reflections() < 1:
            print("\nPrimary reflection not yet defined.")
        else:
            (hkl, pos, wl) = self.sample.get_ref0()
            hstr = ["{0:s}".format(self._motor_names[name]) for name in self.axis_names]
            pstr = ["{0:.4f}".format(pos[name]) for name in self.axis_names]
            print(("\nPrimary Reflection (at lambda {0:.4f}):".format(wl)))
            print(("{0:>26s} = {1}".format(" ".join(hstr), " ".join(pstr))))
            print(("{0:>26s} = {1} {2} {3}".format("H K L", *hkl)))

        if self.sample.get_n_reflections() < 2:
            print("\nSecondary reflection not yet defined.")
        else:
            (hkl, pos, wl) = self.sample.get_ref1()
            hstr = ["{0:s}".format(self._motor_names[name]) for name in self.axis_names]
            pstr = ["{0:.4f}".format(pos[name]) for name in self.axis_names]
            print(("\nSecondary Reflection (at lambda {0:.4f}):".format(wl)))
            print(("{0:>26s} = {1}".format(" ".join(hstr), " ".join(pstr))))
            print(("{0:>26s} = {1} {2} {3}".format("H K L", *hkl)))

        print("\nLattice Constants (lengths / angles):")
        print(
            (
                "{0:>26s} = {1:.3f} {2:.3f} {3:.3f} / {4:.3f} {5:.3f} {6:.3f}".format(
                    "real space", *self.sample.get_lattice()
                )
            )
        )
        print(
            (
                "{0:>26s} = {1:.3f} {2:.3f} {3:.3f} / {4:.3f} {5:.3f} {6:.3f}".format(
                    "reciprocal space", *self.sample.get_reciprocal_lattice()
                )
            )
        )

        print(
            "\nLambda = {0:.5f}  Energy = {1:.3f} keV".format(
                self.wavelength, self.energy
            )
        )

    def check_all_hkl(self, h, k, l):  # noqa: E741
        self._geometry.set_pseudo_pos({"hkl_h": h, "hkl_k": k, "hkl_l": l})
        calc_pos_all = self._geometry._engines["hkl"].get_solutions()
        self._geometry.set_axis_pos(calc_pos_all[0])
        calc_pseudo = self._geometry.get_pseudo_pos()
        print("\nCalculated Positions:\n")
        print(
            "H K L = {pos[hkl_h]:f} {pos[hkl_k]:f} {pos[hkl_l]:f}\n\n".format(
                pos=calc_pseudo
            )
        )
        axis_names = self._geometry.get_axis_names()
        print(
            " ".join(
                [
                    "{0:>10.10s}".format(self._motor_names.get(name, name))
                    for name in axis_names
                ]
            )
        )
        for axis_pos in calc_pos_all:
            print(" ".join(["{0:10.4f}".format(axis_pos[name]) for name in axis_names]))
