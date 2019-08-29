# Copyright 2019 Smarter Grid Solutions
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Simple simulator for a solar unit."""

from datetime import datetime
import uuid
from .message import set_phase_a_mmxu
from .single_phase_meter import SinglePhaseMeter
import commonmodule_pb2 as cm
import solarmodule_pb2 as sm


class SinglePhaseSolar(SinglePhaseMeter):
    """A simulated solar on a single phase.

    This is very much like a meter, except that the meter automatically
    turns off when the solar is open.
    """

    def __init__(self, cond_equip_mrid: uuid.UUID = None,
                 cond_equip_name: str = None):
        """Construct a new instance of this breaker model.

        :param cond_equip_mrid: The MRID of the conducting unit.
        :param cond_equip_name: The name of the conducting unit.
        """
        super().__init__(cond_equip_mrid, cond_equip_name)

        gcmk = cm.GridConnectModeKind
        self._connect_mode = gcmk.GridConnectModeKind_CSI

    def to_profiles(self):
        """Get all of the profiles that this generates."""
        srp = sm.SolarReadingProfile()
        equipment = srp.solarInverter.conductingEquipment
        equipment.mRID = str(self.mrid)
        equipment.namedObject.name.value = self.name
        srp.solarReading.CopyFrom(self.to_reading())
        yield srp

        ssp = sm.SolarStatusProfile()
        equipment = ssp.solarInverter.conductingEquipment
        equipment.mRID = str(self.mrid)
        equipment.namedObject.name.value = self.name

        ssp.solarStatus.solarStatusZGEN.GriMod.setVal = self.connect_mode

        zget = ssp.solarStatus.solarStatusZGEN.solarEventAndStatusZGEN
        zget.AuxPwrSt.stVal = True
        zget.DynamicTest.stVal = 0
        zget.EmgStop.stVal = False
        yield ssp

    def to_reading(self):
        """Get the recloser reading profile information for this model."""
        with self.lock:
            self.update_mmtr(datetime.utcnow())

            sr = sm.SolarReading()
            self.to_mmxu(sr.readingMMXU)
            self.to_mmtr(sr.readingMMTR)

        return sr

    def to_mmxu(self, mmxu):
        """Write the MMXU data into the specified structure."""
        gcmk = cm.GridConnectModeKind
        if (self.connect_mode != gcmk.GridConnectModeKind_none):
            super().to_mmxu(mmxu)
        else:
            now = datetime.now()
            mmxu_dict = {
                "A": 0,
                "Hz": 0,
                "PF": 1,
                "PFSign": 0,
                "V": 0,
                "VA": 0,
                "VAr": 0,
                "W": 0
            }
            set_phase_a_mmxu(mmxu, mmxu_dict, now)

    def update_mmtr(self, now):
        """Update the present net energy values."""
        gcmk = cm.GridConnectModeKind
        if (self.connect_mode != gcmk.GridConnectModeKind_none):
            # We only actually update the values if the position is closed
            super().update_mmtr(now)
        else:
            # Nevertheless, this is our last updated time, so that if we are
            # later closed, we update from the last updated time
            self.last_update = now

    def update_profile(self, control):
        """Update this device with the control request."""
        mode = control.solarControl.solarControlFSCC\
            .solarControlScheduleFSCH.ValDCSG.crvPts[0].Pos.ctlVal

        self.connect_mode = mode

    @property
    def connect_mode(self):
        """Get the connect mode kind."""
        return self._connect_mode

    @connect_mode.setter
    def connect_mode(self, value):
        """Set the connect mode kind."""
        self._connect_mode = value

        # We need to update this so that we start re-calculating the
        # the measurements according to this change in status. That is
        # if we just opened, then we cannot have any current or
        # power flowing.
        self.update_mmtr(datetime.utcnow())
