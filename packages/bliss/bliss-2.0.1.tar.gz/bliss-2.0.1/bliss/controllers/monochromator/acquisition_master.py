# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
???
"""

import numpy
import gevent

from bliss.scanning.chain import AcquisitionMaster
from bliss.scanning.channel import AcquisitionChannel, AxisAcquisitionChannel
from bliss.common.motor_group import Group
from bliss.controllers.motors.icepap import Icepap
from bliss.common.utils import (  # noqa: F401
    ColorTags,
    BOLD,
    GREEN,
    YELLOW,
    BLUE,
    RED,
    ORANGE,
)


class TrajectoryEnergyTrackerMaster(AcquisitionMaster):
    def __init__(
        self,
        mono,
        Estart,
        Estop,
        npoints,
        time_per_point,
        trajectory_mode,  # energy/bragg/undulator
        undulator_master=None,
        trigger_type=AcquisitionMaster.SOFTWARE,
        **keys,
    ):

        # Monochromator
        self.mono = mono

        # Scan parameters
        self.Estart = Estart
        self.Estop = Estop
        self.time_per_point = time_per_point
        self.scan_time = float(npoints * self.time_per_point)
        self.trajectory_mode = trajectory_mode

        self.movables_params = {}

        # Motors
        self.trajectory_axis = self.mono._motors["trajectory"]
        if trajectory_mode == "undulator":
            if undulator_master is None:
                raise RuntimeError("No undulator master specified")
            self.tracker_master_axis = undulator_master
        else:
            self.tracker_master_axis = None

        # Build list of motors which will move
        # Theoretical energy
        # There is always a trajectory, at least for the virtual energy axis
        movables = [self.trajectory_axis]
        # Add undulator master axis if trajectory mode is undulator
        if self.tracker_master_axis is not None:
            movables.append(self.tracker_master_axis)
        # Add trackers without trajectory.
        # register them for start/stop/speed/acc calculations
        self.tracked_list = []
        for mot in self.mono.tracking._motors.values():
            if mot != self.tracker_master_axis:
                if mot.tracking.state:
                    if not isinstance(mot.controller, Icepap):
                        movables.append(mot)
                        self.tracked_list.append(mot)

        # Acquisition master will create in the attribute .device
        # a Group object with all motors to be moved
        super().__init__(
            self.trajectory_axis, trigger_type=trigger_type, npoints=npoints, **keys
        )

        self._mot_group = Group(*movables)

        # Create channels for all moving motors
        self.channels.extend((AxisAcquisitionChannel(mot) for mot in movables))

        # Add a channel for theoretical energy
        # "axis:" prefix allow flint to recognize it as plotable.
        self.channels.extend(
            (AcquisitionChannel("axis:Energy", numpy.double, (), unit="KeV"),)
        )

        # Calculate parameters (speed/acc/start/stop) for all moving motors
        self.calc_param()

    def prepare(self):
        # Move to start position
        movement = []
        for name in self.movables_params.keys():
            movement.append(self.movables_params[name]["axis"])
            movement.append(self.movables_params[name]["start"])
        self._mot_group.move(*movement)

    def start(self):
        if self.parent:
            return
        self.trigger()

    def trigger(self):
        try:
            # Emit theoretical position for all motors
            for channel in self.channels:
                channel.emit(self.position_list[channel.short_name])

            # Set speed and acceleration for concerned motors
            self.set_speed_acc()

            # Move to end position
            movement = []
            for name in self.movables_params.keys():
                axis = self.movables_params[name]["axis"]
                pos = self.movables_params[name]["stop"]
                movement.append(axis)
                movement.append(pos)
                # print(RED(f"START MOVE {axis.name} TO {pos}"))
            self._mot_group.move(*movement)
        finally:
            self.unset_speed_acc()

    def stop(self):
        self._mot_group.stop()
        self.unset_speed_acc()

    def get_acc_vel_from_acc_max(self, motor, startv, stopv):
        res = {}
        res["axis"] = motor
        res["vel"] = abs(stopv - startv) / self.scan_time
        res["acc"] = motor.acceleration
        res["acct"] = res["vel"] / res["acc"]
        res["accd"] = res["vel"] * res["acct"] / 2.0
        res.update(self.get_start_stop(motor, startv, stopv, res["accd"]))
        self.movables_params[motor.name] = res
        self.acceleration_time = res["acct"]

    def get_acc_vel_from_acc_time(self, motor, startv, stopv):
        res = {}
        res["axis"] = motor
        res["vel"] = abs(stopv - startv) / self.scan_time
        res["acct"] = self.acceleration_time
        res["acc"] = res["vel"] / res["acct"]
        res["accd"] = res["vel"] * res["acct"] / 2.0
        res.update(self.get_start_stop(motor, startv, stopv, res["accd"]))
        self.movables_params[motor.name] = res
        return res

    def get_start_stop(self, motor, startv, stopv, accd):
        res = {}
        res["vel_old"] = motor.velocity
        res["acc_old"] = motor.acceleration
        if startv < stopv:
            res["start"] = startv - accd
            res["stop"] = stopv + accd
        else:
            res["start"] = startv + accd
            res["stop"] = stopv - accd
        return res

    def _check_undulator_speed(self, axis):
        real_velocity = axis.velocity
        if self.velocity != real_velocity:
            track_start = axis.tracking.energy2tracker(self.Estart)
            track_stop = axis.tracking.energy2tracker(self.Estop)

            new_scan_time = numpy.abs(track_start - track_stop) / real_velocity
            new_int_time = new_scan_time / self.npoints

            print(GREEN(f'"{axis.name}" Optimal Int. Time (s): {new_int_time}'))

    def calc_param(self):
        set_energy_start = self.Estart
        set_energy_stop = self.Estop

        # All theretical positions for moving motors will be calculated
        self.position_list = {}

        # Energy Position
        energy_pos = numpy.linspace(self.Estart, self.Estop, self.npoints + 1)

        # Doing weird stuff to respond to scientific question
        delta = (self.Estop - self.Estart) / (2 * self.npoints)
        self.position_list["Energy"] = numpy.linspace(
            self.Estart - delta, self.Estop - delta, self.npoints + 1
        )
        self.position_list["Energy"][0] = self.Estart

        # Trajectory axis
        if self.trajectory_mode == "energy":
            # Ennergy Trajectory
            self.position_list[self.trajectory_axis.name] = energy_pos
            self.acceleration_time = (
                1.01 * self.trajectory_axis._get_min_acceleration_time()
            )
            self.get_acc_vel_from_acc_time(
                self.trajectory_axis,
                self.Estart,
                self.Estop,
            )
            self.undershoot = self.movables_params[self.trajectory_axis.name]["accd"]
            self.velocity = self.movables_params[self.trajectory_axis.name]["vel"]
        elif self.trajectory_mode == "bragg":
            # Bragg Trajectory
            self.position_list[self.trajectory_axis.name] = self.mono.energy2bragg(
                energy_pos
            )
            self.get_acc_vel_from_acc_max(
                self.trajectory_axis,
                self.mono.energy2bragg(self.Estart),
                self.mono.energy2bragg(self.Estop),
            )
            self.undershoot = self.movables_params[self.trajectory_axis.name]["accd"]
            self.velocity = self.movables_params[self.trajectory_axis.name]["vel"]
        elif self.trajectory_mode == "undulator":
            # Master tracker
            self.position_list[
                self.tracker_master_axis.name
            ] = self.tracker_master_axis.tracking.energy2tracker(energy_pos)

            virtual_motor = self.mono._motors["virtual_energy"]
            virtual_name = virtual_motor.name
            virtual_steps_per_unit = virtual_motor.steps_per_unit

            set_energy_start = self.Estart * virtual_steps_per_unit
            ind = (
                numpy.searchsorted(
                    self.mono._traj_dict[virtual_name],
                    [
                        set_energy_start,
                    ],
                    side="left",
                )[0]
                - 1
            )
            undu_start = self.mono._traj_data[ind]

            set_energy_stop = self.Estop * virtual_steps_per_unit
            ind = numpy.searchsorted(
                self.mono._traj_dict[virtual_name],
                [
                    set_energy_stop,
                ],
                side="left",
            )[0]
            undu_stop = self.mono._traj_data[ind]

            self.get_acc_vel_from_acc_max(
                self.tracker_master_axis,
                undu_start,
                undu_stop,
            )
            self.undershoot = self.movables_params[self.tracker_master_axis.name][
                "accd"
            ]
            self.velocity = self.movables_params[self.tracker_master_axis.name]["vel"]

            # Undulator Trajectory
            self.position_list[self.trajectory_axis.name] = self.position_list[
                self.tracker_master_axis.name
            ]
            self.get_acc_vel_from_acc_time(
                self.trajectory_axis,
                undu_start,
                undu_stop,
            )
        else:
            raise RuntimeError(f'Trajectory mode "{self.trajectory_mode}" unknown')

        # Check if speed/acc are valid for trajectory axis
        vel_max = self.trajectory_axis._get_max_velocity()
        vel = self.movables_params[self.trajectory_axis.name]["vel"]
        if vel > vel_max:
            raise RuntimeError(
                RED(f"Velocity not valid for trajectory: {vel} (max: {vel_max})")
            )

        # Tracked motors without trajectory facility
        if self.tracked_list is not None:
            for axis in self.tracked_list:
                start_pos = axis.tracking.energy2tracker(set_energy_start)
                end_pos = axis.tracking.energy2tracker(set_energy_stop)
                self.position_list[axis.name] = numpy.linspace(
                    start_pos, end_pos, self.npoints + 1
                )
                self.get_acc_vel_from_acc_time(
                    axis,
                    start_pos,
                    end_pos,
                )
                if self.movables_params[axis.name]["acc"] < 0.5:
                    self.movables_params[axis.name]["acc"] = 0.5

    def set_speed_acc(self):
        for key in self.movables_params:
            self.movables_params[key]["axis"].wait_move()
            self.movables_params[key]["axis"].acceleration = self.movables_params[key][
                "acc"
            ]
            self.movables_params[key]["axis"].velocity = self.movables_params[key][
                "vel"
            ]
            self.movables_params[key]["acc_set"] = self.movables_params[key][
                "axis"
            ].acceleration
            self.movables_params[key]["vel_set"] = self.movables_params[key][
                "axis"
            ].velocity
            self._check_undulator_speed(self.movables_params[key]["axis"])

    def unset_speed_acc(self):
        for key in self.movables_params:
            self.movables_params[key]["axis"].wait_move()

            while self.movables_params[key]["axis"].state.MOVING:
                gevent.sleep(0.1)

            self.movables_params[key]["axis"].acceleration = self.movables_params[key][
                "acc_old"
            ]
            self.movables_params[key]["axis"].velocity = self.movables_params[key][
                "vel_old"
            ]

        return True
