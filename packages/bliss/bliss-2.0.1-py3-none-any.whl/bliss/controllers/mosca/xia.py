# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import os
import numpy
import enum
from bliss.common.tango import DevFailed
from bliss.controllers.mosca.base import McaController, TriggerMode

DetectorMode = enum.Enum("DetectorMode", "MCA MAP")


class FalconX(McaController):

    MCA_REFRESH_RATE_LIMIT = 0.01

    STATS_MAPPING = {
        # MOSCA    :  NxWriter
        "output": "events",
        "icr": "icr",
        "ocr": "ocr",
        "livetime": "trigger_livetime",
        "deadtime": "deadtime",
        "realtime": "realtime",
        "triggers": "triggers",
        "livetime_events": "energy_livetime",
        "deadtime_correction": "deadtime_correction",
    }

    def __info__(self):
        txt = super().__info__()
        txt += f" detector mode:     {self.hardware.detector_mode}\n"
        txt += f" refresh rate:      {self.hardware.refresh_rate:.4f} s\n"

        txt += f"\n configuration file: {self.configuration_file}\n"
        return txt

    def _load_settings(self):
        super()._load_settings()

        # load last configuration file
        config_path = self._settings.get("config_path")
        if config_path:
            fdir, fname = os.path.split(config_path)
            try:
                self.hardware.config_path = fdir
                self.hardware.config = fname
            except DevFailed as e:
                print("cannot load last configuration file:", e.args[0].desc)
                self._settings["config_path"] = None
        else:
            config_path = self.configuration_file
            self._settings["config_path"] = config_path

    def _prepare_acquisition(self, acq_params):

        self.hardware.trigger_mode = acq_params["trigger_mode"]
        self.hardware.number_points = acq_params["npoints"]

        preset_time = acq_params["preset_time"]  # seconds

        if acq_params["trigger_mode"] == TriggerMode.SOFTWARE.name:

            # use given refresh_rate or 100ms by default
            refresh_rate = acq_params.setdefault("refresh_rate", 0.1)  # seconds

            # adjust refresh_rate if preset_time is smaller
            if preset_time <= refresh_rate:
                acq_params["refresh_rate"] = refresh_rate = preset_time

            self.refresh_rate = refresh_rate
            self.hardware.preset_value = preset_time * 1000  # milliseconds

        else:

            refresh_rate = acq_params.get("refresh_rate")  # seconds
            if refresh_rate is None:
                refresh_rate = self.hardware.refresh_rate
            else:
                self.refresh_rate = refresh_rate

            # auto tune number of pixels per buffer
            if preset_time <= 2 * refresh_rate:
                ppb_mini = int(numpy.ceil(2 * refresh_rate / preset_time)) + 1
            else:
                ppb_mini = 1

            ppb_default = max(ppb_mini, int(refresh_rate / preset_time))

            ppb = acq_params.get("map_pixels_per_buffer", ppb_default)

            # print(
            #     f"=== ppb={ppb}, ppb_mini={ppb_mini}, rate={refresh_rate}, time={acq_params['preset_time']}"
            # )

            self.hardware.map_pixels_per_buffer = ppb

    @property
    def refresh_rate(self):
        return self.hardware.refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, value):
        if self.hardware.detector_mode == DetectorMode.MCA.name:
            if value < self.MCA_REFRESH_RATE_LIMIT:
                raise ValueError(
                    f"refresh rate must be >= {self.MCA_REFRESH_RATE_LIMIT}s in SOFTWARE trigger mode"
                )
        self.hardware.refresh_rate = value

    @property
    def detectors_identifiers(self):
        """return active detectors identifiers list [str] (['module:channel_in_module', ...])"""
        return self.hardware.channels_module_and_index

    @property
    def detectors_aliases(self):
        """return active detectors channels aliases list [int]"""
        return self.hardware.channels_alias

    @property
    def configuration_file(self):
        fdir = self.hardware.config_path
        fname = self.hardware.config
        return os.path.join(fdir, fname)

    @configuration_file.setter
    def configuration_file(self, fpath):
        fdir, fname = os.path.split(fpath)
        doreload = False
        if fdir:
            if fdir != self.hardware.config_path:
                self.hardware.config_path = fdir
                doreload = True
        if fname:
            if fname != self.hardware.config:
                self.hardware.config = fname
                doreload = True

        self._settings["config_path"] = self.configuration_file

        if doreload:
            self.initialize()
