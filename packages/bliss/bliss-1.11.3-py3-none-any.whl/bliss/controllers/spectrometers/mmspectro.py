# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numpy

from bliss.common.utils import autocomplete_property
from bliss.controllers.spectrometers.spectro_base import (
    Analyser,
    Detector,
    Spectrometer,
)
from bliss.controllers.spectrometers.spectro_base import get_angle, direction_to_angles


class MMAnalyser(Analyser):
    def _load_settings(self):
        """Get from redis the dict of persistent spectrometer parameters (redis access)"""
        cached = super()._load_settings()
        cached["det_deviation_x"] = self._settings.get("det_deviation_x", 0)
        cached["a_z_set"] = self._settings.get("a_z_set", 0)
        return cached

    def _get_pos(self, tag):
        """return one of the position coordinates [xpos, ypos, zpos] or
        orientation angles (pitch, yaw) expressed in the laboratory referential
        (i.e taking into account a possible spectrometer origin != [0,0,0]).
        The returned value must be computed from the actual real axes position to reflect
        actual positioner situation.
        args: tag is one of ["xpos", "ypos", "zpos", pitch, "yaw"]
        """
        ypos = self.config["ypos"]  # + self.referential_origin[1]
        if tag == "rpos":
            x = self._get_real_axis_pos("xpos")
            y = ypos
            return numpy.sqrt(x**2 + y**2)
        elif tag == "ypos":
            return ypos
        elif tag in [
            "xpos",
            "zpos",
        ]:
            return self._get_real_axis_pos(tag)
        elif tag == "pitch":
            return self._get_real_axis_pos("theta") - 90
        elif tag == "yaw":
            return -self._get_real_axis_pos("chi")

        raise RuntimeError(f"unknown tag {tag}")

    def _xes_eh2(self, bragg, a_z_set, det_deviation_x):
        radius = 2 * self.radius
        theta = numpy.deg2rad(bragg)  # convert angles in radians
        alpha = numpy.deg2rad(-self.miscut)

        # ____caculate positions in Rowland frame assuming that detector and sample are placed along vertical line_____
        axvert = radius * numpy.square(
            numpy.sin(theta)
        )  # distance center line sample-detector and symmetric crystal Rowland position
        azvert = radius * numpy.sin(theta) * numpy.cos(theta)
        dzvert = 2 * azvert  # distance sample - detector

        Avec = [
            radius * numpy.sin(theta + alpha) * numpy.sin(theta - alpha),
            0,
            radius * numpy.sin(theta + alpha) * numpy.cos(theta - alpha),
        ]
        Dvec = [0, 0, dzvert]
        Rvec = [
            axvert,
            0,
            azvert,
        ]  # this is needed to define the position of the Rowland circle

        rot_alpha = numpy.array(
            [
                [numpy.cos(-alpha), 0, numpy.sin(-alpha)],
                [0, 1, 0],
                [-numpy.sin(-alpha), 0, numpy.cos(-alpha)],
            ]
        )
        CvecNorm = rot_alpha.dot([-1, 0, 0])  # norm on crystal plane
        AvecNorm = rot_alpha.dot(CvecNorm)  # norm on crystal optical surface
        RvecNorm = [-1, 0, 0]

        y_angle = numpy.arcsin(self.ypos / Avec[0])  # phi rotation in vertical position
        rot_z = numpy.array(
            [
                [numpy.cos(y_angle), -numpy.sin(y_angle), 0],
                [numpy.sin(y_angle), numpy.cos(y_angle), 0],
                [0, 0, 1],
            ]
        )
        Avec = rot_z.dot(Avec)
        Dvec = rot_z.dot(Dvec)
        Rvec = rot_z.dot(Rvec)
        CvecNorm = rot_z.dot(CvecNorm)
        AvecNorm = rot_z.dot(AvecNorm)
        RvecNorm = rot_z.dot(RvecNorm)

        # rotate Rowland frame such that az becomes a_z_set defined as
        # position of center of analyzer crystal
        if (
            a_z_set != -1
        ):  # choose -1 if you do not want to rotate around y axis. This is only for testing and not an option in the EH2 spectrometer
            theta_z_off = numpy.arcsin(a_z_set / radius * numpy.sin(theta + alpha))
            z_angle = (
                numpy.pi / 2 - theta + alpha - theta_z_off
            )  # rotation to have crystal at zoffvec(1). Positive alpha gives positive azoff
            rot_y = numpy.array(
                [
                    [numpy.cos(z_angle), 0, numpy.sin(z_angle)],
                    [0, 1, 0],
                    [-numpy.sin(z_angle), 0, numpy.cos(z_angle)],
                ]
            )
            Avec = rot_y.dot(Avec)
            Dvec = rot_y.dot(Dvec)
            Rvec = rot_y.dot(Rvec)
            CvecNorm = rot_y.dot(CvecNorm)
            AvecNorm = rot_y.dot(AvecNorm)
            RvecNorm = rot_y.dot(RvecNorm)

        DvecNorm = numpy.subtract(Avec, Dvec)
        DvecNorm = DvecNorm / numpy.linalg.norm(DvecNorm)

        theta_ana = get_angle(AvecNorm, [0, 0, 1])
        chi_ana = get_angle([AvecNorm[0], AvecNorm[1], 0], [-1, 0, 0]) * numpy.sign(
            AvecNorm[1]
        )  # angle in the xy plane
        dth = get_angle(DvecNorm, [-1, 0, 0])

        d = self._lab_to_positioner_matrix(Avec) @ AvecNorm
        pitch, yaw = direction_to_angles(d)

        # apply deviation of detector position. Definition in agreement with ID26 ray tracing code
        # print('det_deviation_x',det_deviation_x)
        det_deviation = det_deviation_x / numpy.cos(numpy.pi - dth)
        Dvec = Dvec + DvecNorm * det_deviation

        return [
            Avec,
            Dvec,
            Rvec,
            pitch,
            yaw,
            numpy.rad2deg(theta_ana),
            numpy.rad2deg(chi_ana),
            numpy.rad2deg(dth),
        ]

    @property
    def a_z_set(self):
        return self._get_setting("a_z_set")

    @a_z_set.setter
    def a_z_set(self, value):
        self._set_setting("a_z_set", value)
        self._update()

    @property
    def det_deviation_x(self):
        return self._get_setting("det_deviation_x")

    @det_deviation_x.setter
    def det_deviation_x(self, value):
        self._set_setting("det_deviation_x", value)
        self._update()

    def compute_bragg_solution(self, bragg):
        """returns a tuple (bragg, bragg_solution, reals_positions):
        - bragg: the bragg angle associated to this solution.
        - bragg_solution: a dict with relevant data for the position and orientation of this positioner.
          Data expressed in the laboratory referential with an origin at (0,0,0) (i.e. ignoring self.referential_origin).
        - reals_positions: the theoritical positions of the real axes for the given bragg value.
          Reals positions expressed in laboratory referential (must take into account self.referential_origin!=(0,0,0))
        """
        [Avec, Dvec, Rvec, pitch, yaw, theta_ana, chi_ana, dth] = self._xes_eh2(
            bragg, self.a_z_set, self.det_deviation_x
        )

        reals_pos = {}
        reals_pos["xpos"] = Avec[0]  # + self.referential_origin[0]
        reals_pos["zpos"] = Avec[2]  # + self.referential_origin[2]
        reals_pos["theta"] = theta_ana
        reals_pos["chi"] = chi_ana

        return (
            bragg,
            {
                "Ai": Avec,
                "Di": Dvec,
                "Ri": Rvec,
                "pitch": pitch,
                "yaw": yaw,
                "theta_ana": theta_ana,
                "chi_ana": chi_ana,
                "dth": dth,
            },
            reals_pos,
        )

    def scan_metadata(self):
        meta_dict = {"@NX_class": "NXcollection"}
        meta_dict["crystal"] = str(self.xtal_sel)
        meta_dict["miscut"] = self.miscut
        meta_dict["radius"] = self.radius
        meta_dict["referential_origin"] = self.referential_origin
        meta_dict["offset_on_detector"] = self.offset_on_detector
        meta_dict["det_deviation_x"] = self.det_deviation_x
        meta_dict["a_z_set"] = self.a_z_set
        return meta_dict


class MMDetector(Detector):
    def __init__(self, config):
        super().__init__(config)

    def _get_pos(self, tag):
        """return one of the position coordinates [xpos, ypos, zpos] or
        orientation angles (pitch, yaw) expressed in the laboratory referential
        (i.e taking into account a possible spectrometer origin != [0,0,0]).
        The returned value must be computed from the actual real axes position to reflect
        actual positioner situation.
        args: tag is one of ["xpos", "ypos", "zpos", pitch, "yaw"]
        """
        # === !!! motor position is expressed in lab ref (so it already includes referential_origin offset) !!!
        ypos = self.config.get("ypos", 0)  # + self.referential_origin[1]
        yaw = self.config.get("yaw", 0)
        if tag == "rpos":
            x = self._get_pos("xpos")
            y = ypos
            return numpy.sqrt(x**2 + y**2)
        elif tag == "ypos":
            return ypos
        elif tag == "yaw":
            return yaw
        elif tag == "xpos":
            dlong_center_x = (
                self.dlong.position * numpy.cos(numpy.deg2rad(self.dlong_angle))
                + self.dlong_base_x
            )
            xpos = self._get_real_axis_pos("dx") + dlong_center_x - self.dx_offset
            return xpos
        elif tag == "zpos":
            dlong_center_z = (
                self.dlong.position * numpy.sin(numpy.deg2rad(self.dlong_angle))
                + self.dlong_base_z
                - self.azlong.position
            )
            zpos = (
                self._get_real_axis_pos("dz")
                + dlong_center_z
                - self.dz_offset
                - self.dz_correction
            )
            return zpos
        elif tag == "pitch":
            pitch = 180 - self._get_real_axis_pos("dth")
            return pitch
        raise RuntimeError(f"unknown tag {tag}")

    def _load_config(self):
        super()._load_config()

        self._dlong_angle = self.config.get("dlong_angle", 68)
        self._dlong_travel = self.config.get("dlong_travel", 1200)
        self._dlong_base_x = self.config.get("dlong_base_x", -21.51)
        self._dlong_base_z = self.config.get("dlong_base_z", 160.25)
        self._dx_offset = self.config.get("dx_offset", 150)
        self._dz_offset = self.config.get("dz_offset", 150)

    def _load_settings(self):
        """Get from redis the dict of persistent spectrometer parameters (redis access)"""
        cached = super()._load_settings()
        cached["dz_correction"] = self._settings.get("dz_correction", 0)
        return cached

    def _dx_dz_calc(self, Dvec, dlong_pos):

        dx = Dvec[0]
        dz = Dvec[2]

        dlong_angle = numpy.deg2rad(self.dlong_angle)
        dlong_base_x = self.dlong_base_x
        dlong_base_z = self.dlong_base_z - self.azlong.position

        dlong_center_x = dlong_pos * numpy.cos(dlong_angle) + dlong_base_x
        dlong_center_z = dlong_pos * numpy.sin(dlong_angle) + dlong_base_z

        stage_dx_pos = dx - dlong_center_x + self.dx_offset
        stage_dz_pos = dz - dlong_center_z + self.dz_offset + self.dz_correction

        return stage_dx_pos, stage_dz_pos

    def _dlong_calc(self, theta):

        dvec = self.target._xes_eh2(
            theta, self.target.a_z_set, self.target.det_deviation_x
        )[1]

        dx = dvec[0]
        dz = dvec[2]

        dlong_angle = numpy.deg2rad(self.dlong_angle)
        dlong_travel = self.dlong_travel
        dlong_base_x = self.dlong_base_x
        dlong_base_z = self.dlong_base_z - self.azlong.position

        dlong_low_limit = self.dlong.low_limit
        dlong_high_limit = self.dlong.high_limit
        if dlong_low_limit > dlong_high_limit:
            dlong_low_limit, dlong_high_limit = dlong_high_limit, dlong_low_limit

        # make lines for dlong stage and m=-1 through detector point
        m = numpy.tan(dlong_angle)
        b = dlong_base_z - dlong_base_x * m
        mn = numpy.tan(numpy.deg2rad(-45))
        bn = dz - mn * dx

        # calculate intersection point between dlong and m-1 line: This is where dlong will be driven.
        dlong_center_x = (bn - b) / (m - mn)
        dlong_center_z = m * dlong_center_x + b

        dlong_center_x = max(dlong_center_x, dlong_base_x)
        dlong_center_x = min(
            dlong_center_x, dlong_travel * numpy.cos(dlong_angle) + dlong_base_x
        )
        dlong_center_z = (
            dlong_base_z if dlong_center_z < dlong_base_x else dlong_center_z
        )
        dlong_center_z = min(
            dlong_center_z, dlong_travel * numpy.sin(dlong_angle) + dlong_base_z
        )

        dlong_pos = (dlong_center_z - dlong_base_z) / numpy.sin(
            dlong_angle
        )  # This may be unnecessary as it is already done before if base is the lowest possible position

        if dlong_pos < dlong_low_limit:
            print(
                "WARNING: Hitting low software limit on dlong. Recalculating dlong positions."
            )
            dlong_pos = dlong_low_limit + 1
            dlong_center_x = dlong_pos * numpy.cos(dlong_angle) + dlong_base_x
            dlong_center_z = dlong_pos * numpy.sin(dlong_angle) + dlong_base_z

        if dlong_pos > dlong_high_limit:
            print(
                "WARNING: Hitting high sofware limit on dlong. Recalculating dlong positions."
            )
            dlong_pos = dlong_high_limit - 1
            dlong_center_x = dlong_pos * numpy.cos(dlong_angle) + dlong_base_x
            dlong_center_z = dlong_pos * numpy.sin(dlong_angle) + dlong_base_z

        print(f"dlong distance from base is {dlong_pos:.2f}")
        print(f"distance x from base is {dlong_center_x:.2f}")
        print(f"distance z from base is {dlong_center_z:.2f}")

        stage_dx_pos, stage_dz_pos = self._dx_dz_calc(dvec, dlong_pos)

        print(f"stage dx at {stage_dx_pos:.2f}")
        print(f"stage dz at {stage_dz_pos:.2f}\n")

        return dlong_pos, dvec

    @Detector.target.setter
    def target(self, value):
        if not isinstance(value, MMAnalyser):
            raise ValueError(f"target {value} is not an MMAnalyser object")
        self._target = value
        self._update()

    @property
    def dlong_angle(self):
        return self._dlong_angle

    @property
    def dlong_travel(self):
        return self._dlong_travel

    @property
    def dlong_base_x(self):
        return self._dlong_base_x

    @property
    def dlong_base_z(self):
        return self._dlong_base_z

    @autocomplete_property
    def dlong(self):
        return self.real_axes["dlong"]

    @autocomplete_property
    def azlong(self):
        return self.real_axes["azlong"]

    @property
    def dx_offset(self):
        return self._dx_offset

    @dx_offset.setter
    def dx_offset(self, value):
        self._dx_offset = value
        self._update()

    @property
    def dz_offset(self):
        return self._dz_offset

    @dz_offset.setter
    def dz_offset(self, value):
        self._dz_offset = value
        self._update()

    @property
    def dz_correction(self):
        return self._get_setting("dz_correction")

    @dz_correction.setter
    def dz_correction(self, value):
        self._set_setting("dz_correction", value)
        self._update()

    def dlong_calc_middle(self, th_1, th_2):
        """
        required if dlong is not moved during scans. The scan range is between low and high.
        A middle position is determined for dlong which is used itself to calculate the motor positions for stage_dx and stage_dz
        """

        th_low = min(th_1, th_2)
        th_high = max(th_1, th_2)

        print(f"at low angle {th_low}")
        pos_lo, dvec_lo = self._dlong_calc(th_low)
        print(f"at high angle {th_high}")
        pos_hi, dvec_hi = self._dlong_calc(th_high)

        pos_middle = abs(pos_hi - pos_lo) / 2 + min(pos_hi, pos_lo)

        print(f"dlong at low angle at {pos_lo:.2f}")
        print(f"dlong at high angle at {pos_hi:.2f}")
        print(f"dlong middle position is at {pos_middle:.2f}")

        try:
            _dx_pos_lo, _dz_pos_lo = self._dx_dz_calc(dvec_lo, pos_middle)
            _dx_pos_hi, _dz_pos_hi = self._dx_dz_calc(dvec_hi, pos_middle)

            def _check_lim(range, value):
                if value == min(list(range) + [value]):
                    return f"- OUT OF RANGE {range}"
                if value == max(list(range) + [value]):
                    return f"- OUT OF RANGE {range}"
                return ""

            print("\nFor this middle position of dlong we get:")
            print(
                f'stage dx at low angle at {_dx_pos_lo:.2f} {_check_lim(self.real_axes["dx"].limits, _dx_pos_lo)}'
            )
            print(
                f'stage dx at high angle at {_dx_pos_hi:.2f} {_check_lim(self.real_axes["dx"].limits, _dx_pos_hi)}'
            )
            print(
                f'stage dz at low angle at {_dz_pos_lo:.2f} {_check_lim(self.real_axes["dz"].limits, _dz_pos_lo)}'
            )
            print(
                f'stage dz at high angle at {_dz_pos_hi:.2f} {_check_lim(self.real_axes["dz"].limits, _dz_pos_hi)}'
            )

        except RuntimeError as e:
            print(e.args[0])

        return pos_middle

    def compute_bragg_solution(self, bragg):
        """returns a tuple (bragg, bragg_solution, reals_positions):
        - bragg: the bragg angle associated to this solution.
        - bragg_solution: a dict with relevant data for the position and orientation of this positioner.
          Data expressed in the laboratory referential with an origin at (0,0,0) (i.e. ignoring self.referential_origin).
        - reals_positions: the theoritical positions of the real axes for the given bragg value.
          Reals positions expressed in laboratory referential (must take into account self.referential_origin!=(0,0,0))
        """
        bsolution = self.target.compute_bragg_solution(bragg)[1]
        pitch, _ = direction_to_angles(bsolution["Ai"] - bsolution["Di"])
        dx, dz = self._dx_dz_calc(bsolution["Di"], self.dlong.position)

        reals_pos = {}
        reals_pos["dx"] = dx  # + self.referential_origin[0]
        reals_pos["dz"] = dz  # + self.referential_origin[2]
        reals_pos["dth"] = bsolution["dth"]
        reals_pos["dlong"] = self.dlong.position
        reals_pos["azlong"] = self.azlong.position

        return (
            bragg,
            {"Di": bsolution["Di"], "pitch": pitch, "dth": bsolution["dth"]},
            reals_pos,
        )

    def scan_metadata(self):
        meta_dict = {"@NX_class": "NXcollection"}
        meta_dict["target"] = self.target.name
        meta_dict["dlong_angle"] = self.dlong_angle
        meta_dict["dlong_travel"] = self.dlong_travel
        meta_dict["dlong_base_x"] = self.dlong_base_x
        meta_dict["dlong_base_z"] = self.dlong_base_z
        meta_dict["dx_offset"] = self.dx_offset
        meta_dict["dz_offset"] = self.dz_offset
        meta_dict["dz_correction"] = self.dz_correction
        return meta_dict


class MMSpectrometer(Spectrometer):
    @Spectrometer.referential_origin.setter
    def referential_origin(self, ref_coords):
        """Define the position [x, y, z] of the spectrometer origin in the laboratory referential"""
        if len(ref_coords) != 3:
            raise ValueError(
                f"origin coordinates must be a vector [x, y, z] not {ref_coords}"
            )
        if list(ref_coords) != [0, 0, 0]:
            raise ValueError("MMSpectrometer origin is fixed to (0,0,0) ")
        self._set_setting("referential_origin", ref_coords)
        for ana in self.analysers:
            ana.referential_origin = ref_coords
        self.detector.referential_origin = ref_coords
        self._update()

    def dlong_calc_middle(self, ene_low, ene_high):
        bragg_min = self.detector.target.energy_calc_controller.energy2bragg(ene_low)
        bragg_max = self.detector.target.energy_calc_controller.energy2bragg(ene_high)
        return self.detector.dlong_calc_middle(bragg_min, bragg_max)

    def dlong_calc(self, energy):
        bragg = self.detector.target.energy_calc_controller.energy2bragg(energy)
        return self.detector._dlong_calc(bragg)[0]
