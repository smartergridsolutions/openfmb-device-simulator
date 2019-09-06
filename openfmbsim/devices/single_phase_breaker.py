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
"""Simple simulator for a breaker unit."""

from datetime import datetime
import uuid
from .message import set_phase_a_mmxu
from .single_phase_meter import SinglePhaseMeter
import breakermodule_pb2 as bm


class SinglePhaseBreaker(SinglePhaseMeter):
    """A simulated breaker on a single phase.

    This is very much like a meter, except that the meter automatically
    turns off when the breaker is open.
    """

    OPEN = 0
    CLOSED = 1

    def __init__(self, cond_equip_mrid: uuid.UUID = None,
                 cond_equip_name: str = None):
        """Construct a new instance of this breaker model.

        :param cond_equip_mrid: The MRID of the conducting unit.
        :param cond_equip_name: The name of the conducting unit.
        """
        super().__init__(cond_equip_mrid, cond_equip_name)

        self._position = SinglePhaseBreaker.CLOSED

    def to_profiles(self):
        """Get all of the profiles that this generates."""
        brp = bm.BreakerReadingProfile()
        equipment = brp.breaker.conductingEquipment
        equipment.mRID = str(self.mrid)
        equipment.namedObject.name.value = self.name
        rr = brp.breakerReading.add()
        rr.CopyFrom(self.to_reading())
        yield brp

        bsp = bm.BreakerStatusProfile()
        equipment = bsp.breaker.conductingEquipment
        equipment.mRID = str(self.mrid)
        equipment.namedObject.name.value = self.name

        position = 1 if self.is_closed else 2
        bsp.breakerStatus.statusAndEventXCBR.Pos.stVal = position
        yield bsp

    def to_reading(self):
        """Get the recloser reading profile information for this model."""
        with self.lock:
            self.update_mmtr(datetime.utcnow())

            br = bm.BreakerReading()
            self.to_mmxu(br.readingMMXU)
            self.to_mmtr(br.readingMMTR)

        return br

    def to_mmxu(self, mmxu):
        """Write the MMXU data into the specified structure."""
        if (self.position == SinglePhaseBreaker.CLOSED):
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
        if (self.position == SinglePhaseBreaker.CLOSED):
            # We only actually update the values if the position is closed
            super().update_mmtr(now)
        else:
            # Nevertheless, this is our last updated time, so that if we are
            # later closed, we update from the last updated time
            self.last_update = now

    def update_profile(self, control):
        """Update this device with the control request."""
        is_closed = control.recloserControl.recloserControlFSCC\
            .switchControlScheduleFSCH.ValDCSG.crvPts[0].Pos.ctlVal

        position = SinglePhaseBreaker.OPEN
        if is_closed:
            position = SinglePhaseBreaker.CLOSED

        self.position = position

    @property
    def position(self):
        """Get the present breaker position."""
        return self._position

    @position.setter
    def position(self, value):
        """Set the recloser position."""
        self._position = value

        # We need to update this so that we start re-calculating the
        # the measurements according to this change in status. That is
        # if we just opened, then we cannot have any current or
        # power flowing.
        self.update_mmtr(datetime.utcnow())

    @property
    def is_closed(self):
        """Get if this recloser is closed."""
        return self.position == SinglePhaseBreaker.CLOSED
