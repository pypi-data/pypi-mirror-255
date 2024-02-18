# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Definition of classes representing a set of common functionalities for
monochromator control.

We assume that a monochromator is composed of:
    - Rotation motor (bragg angle - real motor)
    - Energy motor (Calc Motor)
    - Crystal(s)

The corresponding classes are MonochromatorBase, XtalManager and EnergyCalcMotor.
Configuration examples can be found in:
https://bliss.gitlab-pages.esrf.fr/bliss/master/config_mono.html
"""

import numpy
import tabulate

from bliss.common.types import IterableNamespace
from bliss.common.utils import autocomplete_property
from bliss.common.protocols import HasMetadataForDataset, HasMetadataForScan
from bliss.common.utils import BOLD, BLUE, ORANGE, GREEN
from bliss.config import settings

from bliss.physics.units import ur
from bliss.shell.standard import umv
from bliss.controllers.bliss_controller import BlissController
from bliss.controllers.motor import CalcController
from bliss.controllers.motors.icepap import Icepap

from bliss.controllers.monochromator.xtal import MonochromatorXtals, XtalManager
from bliss.controllers.monochromator.acquisition_master import (
    TrajectoryEnergyTrackerMaster,
)


class Monochromator(BlissController, HasMetadataForScan, HasMetadataForDataset):
    """
    Monochromator
    """

    def __init__(self, config):

        super().__init__(config)

        # Motors
        self._motors = {
            "energy": None,  # Monochromator Energy
            "energy_tracker": None,  # Monochromator Energy + Tracker
            "bragg": None,  # bragg motor (pseudo or real) used in the
            # energy calculations (automatically detected)
            "bragg_real": None,  # Real motor which make the monochromator
            # bragg rotation movement(automatically detected)
            # Used to calculate the energy where the monochromator
            # should be
            "virtual_energy": None,  # Icepap Virtual Energy Axis (trajectory)
            "trajectory": None,  # Trajectory axis
        }

        # Trackers
        tracker = config.get("tracker", None)
        if tracker is not None:
            self.tracking = tracker
            self.tracking._set_mono(self)

        # Trajectory
        # Energy resolution for trajectory (KeV)
        self._traj_resolution = self.config.get("trajectory_resolution", 1e-4)

        # bragg offset used in setE
        self._bragg_offset = settings.SimpleSetting(
            f"Monochromator_{self._name}_bragg_offset", default_value=0.0
        )

        # Tarjectory calculation method according to trajectory mode
        self._trajectory_mode = {
            "bragg": self._get_traj_data_bragg_cst_speed,
            "energy": self._get_traj_data_energy_cst_speed,
            "undulator": self._get_traj_data_undulator_cst_speed,
        }

        """
        Needed to check that trajectory is already loaded
        """
        self._traj_config = {
            "mode": None,
            "start": None,
            "stop": None,
            "points": None,
            "time": None,
        }

    @autocomplete_property
    def motors(self):
        return IterableNamespace(**self._motors)

    def _close(self):
        self.__close__()

    def __close__(self):
        for motor in filter(None, self.motors):
            if hasattr(motor, "__close__"):
                motor.__close__()

    def _load_config(self):
        """Load Configuration"""

        # Motors
        motors_conf = self.config.get("motors", None)
        if motors_conf is None:
            raise ValueError(
                f"Monochromator {BOLD(self._name)}: No Energy motor in config"
            )
        for motor_conf in motors_conf:
            for key in motor_conf.keys():
                motor = motor_conf.get(key)
                self._motors[key] = motor
                if hasattr(motor.controller, "_set_mono"):
                    motor.controller._set_mono(self)

        if self._motors["energy"] is None:
            raise ValueError(
                f"Monochromator {BOLD(self._name)}: No Energy motor in config"
            )
        # Reference Bragg motor and Real bragg motor
        for axis in self._motors["energy"].controller.reals:
            if self._motors["energy"].controller._axis_tag(axis) == "bragg":
                self._motors["bragg"] = axis
        if self._motors["bragg"] is None:
            raise ValueError(
                f"Monochromator {BOLD(self._name)}: Energy motor does not reference Bragg motor"
            )
        rbragg = self._motors["bragg"]
        while isinstance(rbragg.controller, CalcController):
            checked_motor = rbragg
            for axis in checked_motor.controller.reals:
                if checked_motor.controller._axis_tag(axis) == "bragg":
                    rbragg = axis
        self._motors["bragg_real"] = rbragg

        # Xtals Object
        self._load_config_xtal()

    def _load_config_xtal(self):
        self._available_xtals = self.config.get("available_xtals", None)
        self._xtals = self.config.get("xtals", None)
        if self._available_xtals is None:
            if self._xtals is None:
                raise RuntimeError("No xtals configured")
            if len(self._xtals.xtal_names) == 0:
                raise RuntimeError("No Crystals Defined in the XtalManager")
            self._available_xtals = self._xtals.xtal_names
        else:
            if self._xtals is not None:
                if len(self._xtals.xtal_names) == 0:
                    raise RuntimeError("No Crystals Defined in the XtalManager")
                for xtal_name in self._available_xtals:
                    if xtal_name not in self._xtals.xtal_names:
                        raise RuntimeError(
                            f'Xtal "{xtal_name}" not defined in the XtalManager'
                        )
            else:
                xtal_conf = {"name": f"{self.name}_xtals", "xtals": []}
                for xtal_name in self._available_xtals:
                    xtal_conf["xtals"].append({"xtal": xtal_name})
                self._xtals = XtalManager(xtal_conf)
        if len(self._available_xtals) > 1:
            self.xtal = MonochromatorXtals(self, self._available_xtals)

    #
    # Initialization

    def _init(self):
        # Force unit definition for energy and bragg motors
        assert self._motors["energy"].unit, "Please specify unit for the Energy motor"
        assert self._motors["bragg"].unit, "Please specify unit for the Bragg motor"

        # Manage selected xtal
        self._xtal_init()

    def _xtal_init(self):
        """Crystals initializaton"""
        xtal = self._xtals.xtal_sel
        if xtal is not None:
            if not self._xtal_is_in(xtal):
                self._xtals.xtal_sel = None
                for xtal in self._xtals.xtal_names:
                    if self._xtal_is_in(xtal):
                        self._xtals.xtal_sel = xtal
                        return
        else:
            for xtal in self._xtals.xtal_names:
                if self._xtal_is_in(xtal):
                    self._xtals.xtal_sel = xtal
                    return

    #
    # User Info

    def __info__(self):
        print(f"\n{self._get_info_mono()}")
        print(f"\n{self._get_info_xtals()}")
        print(f"\n{self._get_info_motors()}")
        return ""

    def _get_info_mono(self):
        """Get the monochromator information."""
        return f"    Monochromator   : {self._name}"

    def _get_info_xtals(self):
        """Get the crystal information."""
        xtal = self._xtals.xtal_sel
        xtals = " ".join(self._available_xtals)
        mystr = f"    Crystal: {GREEN(xtal)} ({xtals})"
        return mystr
        xtal = self._xtals.xtal_sel
        xtals = " ".join(self._available_xtals)
        if self._xtal_is_in(xtal):
            xtal_str = GREEN(xtal)
        else:
            xtal_str = ORANGE("Unknown")
        mystr = f"Crystal: {xtal_str} ({xtals})\n\n"
        return mystr

    def _get_info_motors(self):
        mystr = self._get_info_motor_energy()
        mystr += "\n\n"
        mystr += self._get_info_motor_calc(self._motors["bragg"])
        mystr += "\n\n"
        mystr += self._get_info_motor_tracking()
        mystr += "\n"
        return mystr

    def _get_info_motor_energy(self):
        # TITLE
        title = [
            "    ",
            "",
            BLUE(self._motors["energy"].name),
        ]
        if isinstance(self._motors["bragg"].controller, CalcController):
            title.append(ORANGE(self._motors["bragg"].name))
        else:
            title.append(BLUE(self._motors["bragg"].name))

        # CALCULATED POSITION ROW
        bragg_pos = (
            self._motors["bragg_real"].sign * self._motors["bragg_real"].dial
            + self.bragg_offset
        )
        bragg_unit = self._motors["bragg"].unit
        energy_pos = self.bragg2energy(bragg_pos)
        energy_unit = self._motors["energy"].unit
        calculated = [
            "    ",
            "Calculated",
            f"{energy_pos:.3f} {energy_unit}",
            f"{bragg_pos:.3f} {bragg_unit}",
        ]
        #
        # CURRENT POSITION ROW
        #
        bragg_pos = self._motors["bragg"].position
        energy_pos = self._motors["energy"].position
        current = [
            "    ",
            "   Current",
            f"{energy_pos:.3f} {energy_unit}",
            f"{bragg_pos:.3f} {bragg_unit}",
        ]
        info_str = tabulate.tabulate(
            [calculated, current], headers=title, tablefmt="plain", stralign="right"
        )
        return info_str

    def _get_info_motor_calc(self, motor):
        info_str = ""
        if isinstance(motor.controller, CalcController):
            controller = motor.controller
            # TITLE
            title = ["    ", ""]
            for axis in controller.pseudos:
                title.append(BLUE(axis.name))
            for axis in controller.reals:
                title.append(ORANGE(axis.name))
            # CURRENT POSITION ROW
            current = ["    ", "   Current"]
            for axis in controller.pseudos:
                current.append(f"{axis.position:.3f} {axis.unit}")
            for axis in controller.reals:
                current.append(f"{axis.position:.3f} {axis.unit}")

            info_str = tabulate.tabulate(
                [current],
                headers=title,
                tablefmt="plain",
                stralign="right",
            )

            for axis in controller.reals:
                if isinstance(axis.controller, CalcController):
                    info_str += "\n\n"
                    info_str += self._get_info_motor_calc(axis)

        return info_str

    def _get_info_motor_tracking(self):
        info_str = ""
        if hasattr(self, "tracking"):
            controller = self._motors["energy_tracker"].controller
            # TITLE
            title = ["    ", ""]
            for axis in controller.pseudos:
                title.append(BLUE(axis.name))
            for axis in controller.reals:
                title.append(ORANGE(axis.name))
            # CALCULATED POSITION ROW
            bragg_pos = (
                self._motors["bragg_real"].sign * self._motors["bragg_real"].dial
                + self.bragg_offset
            )
            energy_dial = self.bragg2energy(
                self._motors["bragg_real"].sign * self._motors["bragg_real"].dial
            )
            energy_pos = self.bragg2energy(bragg_pos)
            calculated = ["    ", "Calculated"]
            valu = self._motors["energy"].unit
            calculated.append(f"{energy_pos:.3f} {valu}")
            for axis in controller.reals:
                if controller._axis_tag(axis) == "energy":
                    calculated.append(f"{energy_pos:.3f} {valu}")
                else:
                    calculated.append(
                        f"{axis.tracking.energy2tracker(energy_dial):.3f} {axis.unit}"
                    )
            # CURRENT POSITION ROW
            current = ["    ", "   Current"]
            current.append(
                f"{controller.pseudos[0].position:.3f} {controller.pseudos[0].unit}"
            )
            for axis in controller.reals:
                current.append(f"{axis.position:.3f} {axis.unit}")
            # TRACKING STATE ROW
            tracking = ["    ", "Tracking", "", ""]
            for axis in controller.reals:
                if controller._axis_tag(axis) != "energy":
                    if axis.tracking.state:
                        tracking.append("ON")
                    else:
                        tracking.append("OFF")

            info_str = tabulate.tabulate(
                [calculated, current, tracking],
                headers=title,
                tablefmt="plain",
                stralign="right",
            )
        return info_str

    #
    # Xtals

    def _xtal_is_in(self, xtal):
        """
        To be overloaded to reflect the monochromator behaviour
        """
        return True

    def _xtal_change(self, xtal):
        """
        To be overloaded to reflect the monochromator behaviour
        """
        pass

    #
    # Energy related methods

    def setE(self, energy):
        """
        For SPEC compatibility:
        This method change the offset of the Bragg motor to fit with an energy
        which has been positioned using a known sample.
        Remarks:
            - The mono need to be at the given energy.
            - In case of the bragg motor being a CalcMotor, do not forget
              to foresee the set offset method in it.
        """
        new_bragg = self.energy2bragg(energy)
        old_bragg = self._motors["bragg"].dial
        self._bragg_offset.set(new_bragg - old_bragg)

        self._motors["bragg"].offset = self._bragg_offset.get()
        self._motors["energy"].controller.sync_pseudos()

    @property
    def bragg_offset(self):
        return float(self._bragg_offset.get())

    def energy2bragg(self, energy):
        """Calculate the bragg angle as function of the energy.
        Args:
            energy(float): Energy value in the units of the energy motor.
        Returns:
            (float): Bragg angle value in the units of the bragg motor
        """
        energy_unit = energy * ur.Unit(self._motors["energy"].unit)
        # convert energy in keV
        energy_keV = energy_unit.to("keV").magnitude
        bragg_deg = self._xtals.energy2bragg(energy_keV) * ur.deg
        # returned bragg angle value is in deg, convert in motor units
        bragg_unit = bragg_deg.to(self._motors["bragg"].unit)
        return bragg_unit.magnitude

    def bragg2energy(self, bragg):
        """Calculate bragg angle for given energy.
        Args:
            bragg (float): Bragg angle value in the units of the bragg motor.
        Retuns:
            (float): Energy value in the units of the energy motor.
        """
        bragg_unit = bragg * ur.Unit(self._motors["bragg"].unit)
        # covert bragg in deg
        bragg_deg = bragg_unit.to("deg").magnitude
        energy_keV = self._xtals.bragg2energy(bragg_deg) * ur.keV
        # returned value is in keV, convert in motor units
        energy_unit = energy_keV.to(self._motors["energy"].unit)
        return energy_unit.magnitude

    #
    # Trajectory

    def _is_trajectory_loaded(
        self, from_ene, to_ene, traj_mode, nb_points, time_per_point
    ):

        if (
            self._traj_config["mode"] == traj_mode
            and self._traj_config["start"] == from_ene
            and self._traj_config["stop"] == to_ene
            and self._traj_config["points"] == nb_points
            and self._traj_config["time"] == time_per_point
        ):
            return True
        else:
            return False

    def _get_traj_data_energy_cst_speed(self):
        self._traj_data = self._ene_data

    def _get_traj_data_bragg_cst_speed(self):
        self._ene_data = numpy.flip(self._ene_data)
        self._traj_data = self.energy2bragg(self._ene_data)

    def _get_traj_data_undulator_cst_speed(self):
        mot = self._undulator_master
        self._traj_data = mot.sign * (
            mot.tracking.energy2tracker(self._ene_data) - mot.offset
        )

    def _load_raw_trajectory(self, Estart, Estop, traj_mode):
        """
        Generic method
        """
        if traj_mode not in self._trajectory_mode.keys():
            traj_mode_list = "/".join(self._trajectory_mode.keys())
            raise RuntimeError(
                f'Unknown trajectory mode "{traj_mode}" ({traj_mode_list})'
            )

        self._traj_dict = {}

        # get_energy_parameter list
        self._get_energy_parameter(Estart, Estop)

        # Calculate trajectory positions
        self._trajectory_mode[traj_mode]()

        # get monochromator trajectory
        traj_mono_dict = self._get_bragg_trajectory(self._ene_data)

        # get trackers trajectories
        traj_tracker_dict = self._get_tracker_trajectory(self._ene_data)

        # get virtual axis trajectory
        traj_virtual_dict = {
            self._motors["virtual_energy"].name: numpy.copy(self._ene_data)
        }

        # set the virtual energy position to the current virtual energy
        bragg_pos = (
            self._motors["bragg_real"].sign * self._motors["bragg_real"].dial
            + self.bragg_offset
        )
        virtual_ene_pos = self.bragg2energy(bragg_pos)
        self._motors["virtual_energy"].dial = virtual_ene_pos
        self._motors["virtual_energy"].offset = 0

        # load trajectory in TrajectoryMotor
        self._traj_dict.update(traj_mono_dict)
        self._traj_dict.update(traj_tracker_dict)
        self._traj_dict.update(traj_virtual_dict)
        self._motors["trajectory"].set_positions(
            self._traj_data, self._traj_dict, self._motors["trajectory"].LINEAR
        )

    def _load_trajectory(
        self,
        from_ene,
        to_ene,
        traj_mode,
        undulator_master=None,
        nb_points=None,
        time_per_point=None,
    ):

        if traj_mode not in self._trajectory_mode.keys():
            mode_str = "/".join(self._trajectory_mode.keys())
            raise RuntimeError(
                f'Trajectory mode "{traj_mode}" does not exist ({mode_str})'
            )

        self._undulator_master = undulator_master

        if not self._is_trajectory_loaded(
            from_ene, to_ene, traj_mode, nb_points, time_per_point
        ):

            # Load a trajectory allowing continuous scan undershoot
            if nb_points is not None and time_per_point is not None:
                self._traj_resolution = 0.001
                self._load_raw_trajectory(from_ene, to_ene, "energy")
                self.master_motor = self._get_monochromator_acquisition_master_motor(
                    from_ene,
                    to_ene,
                    nb_points,
                    time_per_point,
                    "energy",
                    undulator_master,
                )
                Estart_real = from_ene - 3 * self.master_motor.undershoot
                Estop_real = to_ene + 3 * self.master_motor.undershoot

                self._traj_resolution = 0.0001
                self._load_raw_trajectory(Estart_real, Estop_real, traj_mode)

                # Save loaded trajectory
                self._traj_config["mode"] = traj_mode
                self._traj_config["start"] = from_ene
                self._traj_config["stop"] = to_ene
                self._traj_config["points"] = nb_points
                self._traj_config["time"] = time_per_point
        else:
            print(GREEN("Trajectory already loaded"))

    # Get Energy parameter list
    # This method should be re-written in case of complex bragg angle control (ex: Esrf DCM)
    def _get_energy_parameter(self, Estart, Estop):
        nbp = 1 + int(numpy.abs(Estop - Estart) / self._traj_resolution)
        self._ene_data = numpy.linspace(Estart, Estop, nbp)

    # Get position of the bragg motor according to energy parameter list
    # This method should be re-written in case of complex brag angle control (ex: Esrf DCM)
    def _get_bragg_trajectory(self, ene_data):
        data = numpy.copy(ene_data)
        bragg_data = self._motors["bragg"].sign * (
            self.energy2bragg(data) - self.bragg_offset
        )
        mono_dict = {self._motors["bragg"].name: bragg_data}
        return mono_dict

    # Get tracker positions according to energy parameter list
    def _get_tracker_trajectory(self, ene_data):
        data = numpy.copy(ene_data)
        track_dict = {}
        ene_track_mot = self._motors["energy_tracker"]
        for axis in ene_track_mot.controller.reals:
            tag = ene_track_mot.controller._axis_tag(axis)
            if tag != "energy":
                if isinstance(axis.controller, Icepap):
                    track_data = axis.sign * (
                        axis.tracking.energy2tracker(data) - axis.offset
                    )
                    track_dict[axis.name] = track_data
        return track_dict

    def _get_monochromator_acquisition_master_motor(
        self,
        Estart,
        Estop,
        nb_points,
        time_per_point,
        traj_mode,
        undulator_master,
    ):
        """
        in Contscan (/fscan), monochrmator will be pass as a motor.
        It needs to return its AcquisitionMaster object for the scan
        """
        return TrajectoryEnergyTrackerMaster(
            self,
            Estart,
            Estop,
            nb_points,
            time_per_point,
            traj_mode,
            undulator_master=undulator_master,
        )

    #
    # Metadata

    def dataset_metadata(self) -> dict:
        mdata = {"name": self._name}
        xtal = self._xtals.xtal_sel
        if xtal is None:
            return mdata
        theta = self._motors["bragg"].position
        unit = self._motors["bragg"].unit or "deg"
        theta = theta * ur.parse_units(unit)
        mdata.update(self._xtals.get_metadata(theta))
        return mdata

    def scan_metadata(self) -> dict:
        mdata = self.dataset_metadata()
        mdata.pop("name")
        mdata["@NX_class"] = "NXmonochromator"
        if "energy" in mdata:
            mdata["energy@units"] = "keV"
        if "wavelength" in mdata:
            mdata["wavelength@units"] = "m"
        crystal = mdata.get("crystal")
        if crystal:
            crystal["@NX_class"] = "NXcrystal"
            crystal["d_spacing@units"] = "m"
        return mdata


class MonochromatorFixExit(Monochromator):
    """Fixed exit monochromatot"""

    def _load_config(self):
        """Load Configuration"""

        super()._load_config()

        # Fix exit Parameter
        self._fix_exit_offset = self.config.get("fix_exit_offset", None)

    def _info_xtals(self):
        xtal = self._xtals.xtal_sel
        xtals = " ".join(self._available_xtals)
        if hasattr(self, "fix_exit_offset"):
            mystr = f"    Crystal         : {ORANGE(xtal)} ({xtals})\n"
            mystr += f"    Fix exit_offset : {GREEN(self.fix_exit_offset)}"
        else:
            mystr = f"    Crystal : {ORANGE(xtal)} ({xtals})"
        return mystr

    """
    Energy related methods, specific to Fix Exit Mono
    """

    @property
    def fix_exit_offset(self):
        return self._fix_exit_offset

    @fix_exit_offset.setter
    def fix_exit_offset(self, value):
        self._fix_exit_offset = value

    def bragg2dxtal(self, bragg):
        if self.fix_exit_offset is not None:
            dxtal = numpy.abs(self.fix_exit_offset) / (
                2.0 * numpy.cos(numpy.radians(bragg))
            )
            return dxtal
        raise RuntimeError("No Fix Exit Offset parameter defined (config)")

    def dxtal2bragg(self, dxtal):
        if self.fix_exit_offset is not None:
            bragg = numpy.degrees(
                numpy.arccos(numpy.abs(self.fix_exit_offset) / (2.0 * dxtal))
            )
            return bragg
        raise RuntimeError("No Fix Exit Offset parameter defined (config)")

    def energy2dxtal(self, ene):
        bragg = self.energy2bragg(ene)
        dxtal = self.bragg2dxtal(bragg)
        return dxtal


class SimulMonoWithChangeXtalMotors(Monochromator):
    """Simulation monochromator which implements the _xtal_is_in() and
    _xtal_change() to move few motors to configured (YML) positions where a
    single bragg motor can rotate several crystal.
    For instance a multilayer or a channel-cut monochromators can be equiped
    with 2 different crystals and one should shift a vertical and a horizontal
    translation to put the selected crystal into the beam. In addition to the
    translations a offset on the bragg motor is applied to take care of a
    mechanical miss-alignment in angle of the 2 crystal surfaces.
    """

    def _load_config(self):
        """Load Configuration"""

        super()._load_config()

        self._ver_target = {}
        self._hor_target = {}
        self._xtal_bragg_offset = {}

        self._ver_motor = self.config.get("ver_motor")
        self._hor_motor = self.config.get("hor_motor")
        self._ver_tolerance = self.config.get("ver_tolerance")
        self._hor_tolerance = self.config.get("hor_tolerance")
        self._ver_target = self._xtals.get_xtals_config("ver_target")
        self._hor_target = self._xtals.get_xtals_config("hor_target")
        self._xtal_bragg_offset = self._xtals.get_xtals_config("bragg_offset")

    def _xtal_is_in(self, xtal):
        ver_pos = self._ver_motor.position
        hor_pos = self._hor_motor.position

        in_pos = True
        if xtal in self._hor_target.keys():
            if not numpy.isclose(
                hor_pos, self._hor_target[xtal], atol=self._hor_tolerance
            ):
                in_pos = False
        if xtal in self._ver_target.keys():
            if not numpy.isclose(
                ver_pos, self._ver_target[xtal], atol=self._ver_tolerance
            ):
                in_pos = False

        return in_pos

    def _xtal_change(self, xtal):
        mv_list = []
        if xtal in self._hor_target.keys():
            mv_list.append(self._hor_motor)
            mv_list.append(self._hor_target[xtal])
        if xtal in self._ver_target.keys():
            mv_list.append(self._ver_motor)
            mv_list.append(self._ver_target[xtal])

        if xtal in self._xtal_bragg_offset.keys():
            self._motors["bragg"].offset = self._xtal_bragg_offset[xtal]

        if len(mv_list) > 0:
            umv(*mv_list)
