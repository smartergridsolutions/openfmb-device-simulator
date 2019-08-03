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
"""Simple simulator for a battery generation unit."""

from datetime import datetime
import threading
from typing import Iterator
import uuid
from openfmbsim.message import write_timestamp
from openfmbsim.name_generator import make_random_name
import commonmodule_pb2 as cm
import generationmodule_pb2 as gm


def set_cmv(cmv, mag, ang, unit, now: datetime):
    """Set the values in the specified CMV structure.

    :param mag: The value's magnitude.
    :param ang: The value's angle.
    :param unit: The value's unit.
    :param now: The timestamp for the value.
    """
    cmv.cVal.mag.f.value = mag
    cmv.cVal.ang.f.value = ang
    cmv.units.SIUnit = unit
    write_timestamp(cmv.t, now)


def set_bcr(bcr, val, unit, now: datetime):
    """Set the values in the specified BCR structure.

    :param val: The numeric value.
    :param unit: The value's unit.
    :param now: The timestamp for the value.
    """
    bcr.actVal = int(val)
    bcr.units.value = unit
    write_timestamp(bcr.t, now)


class SinglePhaseRealOnlyBattery(object):
    """A simulated single phase battery.

    This is intended to simulate a battery that might be installed in a split
    phase scenario. This is just to keep things simple for the purposes of
    development and integration.

    This also only accounts for real power - you can thus think of this as a
    very simple battery.
    """

    def __init__(self, generating_unit_mrid: uuid.UUID = None,
                 generating_unit_name: str = None):
        """Construct a new instance of this battery model.

        :param generating_unit_mrid: The MRID of the generating unit.
        :param generating_unit_name: The name of the generatoring unit.
        """
        self.mrid = (generating_unit_mrid
                     if generating_unit_mrid is not None
                     else uuid.uuid4())

        self.name = (generating_unit_name
                     if generating_unit_name is not None
                     else make_random_name())

        self.ph_v = 120
        self._w = 1000000
        self.hz = 60

        self.last_update = datetime.utcnow()
        self.dmd_wh = 0
        self.sup_wh = 0

        self.lock = threading.Lock()

    @property
    def device_mrid(self) -> uuid.UUID:
        """Get the ID of the underlying device."""
        return self.mrid

    def control_mrids(self) -> Iterator[uuid.UUID]:
        """Get the MRIDs of the controls in the simulated device."""
        return []

    def to_profiles(self):
        """Get all of the profiles that this generates."""
        gp = gm.GenerationReadingProfile()
        equipment = gp.generatingUnit.conductingEquipment
        equipment.mRID = str(self.mrid)
        equipment.namedObject.name.value = self.name
        gp.generationReading.CopyFrom(self.to_generation_reading())
        yield gp

    def to_generation_reading(self):
        """Get the generation reading profile information for this model."""
        with self.lock:
            self.update_mmtr(datetime.utcnow())

            gr = gm.GenerationReading()
            self.to_mmxu(gr.readingMMXU)
            self.to_mmtr(gr.readingMMTR)

        return gr

    def to_mmxu(self, mmxu):
        """Write the MMXU data into the specified structure."""
        now = datetime.now()
        sk = cm.UnitSymbolKind
        set_cmv(mmxu.A.phsA, self.i_mag, 0, sk.UnitSymbolKind_Amp, now)

        mmxu.Hz.mag.f.value = self.hz
        mmxu.Hz.units.SIUnit = sk.UnitSymbolKind_Hz

        set_cmv(mmxu.PF.phsA, 1, 0, sk.UnitSymbolKind_none, now)

        mmxu.PFSign.setVal = 0

        set_cmv(mmxu.PhV.phsA, self.ph_v, 0, sk.UnitSymbolKind_V, now)
        set_cmv(mmxu.VA.phsA, self.va, 0, sk.UnitSymbolKind_VA, now)
        set_cmv(mmxu.VAr.phsA, 0, 0, sk.UnitSymbolKind_VAr, now)
        set_cmv(mmxu.W.phsA, self.w, 0, sk.UnitSymbolKind_W, now)

    def to_mmtr(self, mmtr):
        """Write the MMTR data into the specified structure."""
        now = datetime.now()
        sk = cm.UnitSymbolKind
        set_bcr(mmtr.DmdWh, self.dmd_wh, sk.UnitSymbolKind_Wh, now)
        set_bcr(mmtr.DmdVArh, 0, sk.UnitSymbolKind_VArh, now)
        set_bcr(mmtr.DmdVAh, self.dmd_wh, sk.UnitSymbolKind_VAh, now)

        set_bcr(mmtr.SupWh, self.sup_wh, sk.UnitSymbolKind_Wh, now)
        set_bcr(mmtr.SupVArh, 0, sk.UnitSymbolKind_VArh, now)
        set_bcr(mmtr.SupVAh, self.sup_wh, sk.UnitSymbolKind_VAh, now)

        total_wh = self.sup_wh - self.dmd_wh
        set_bcr(mmtr.TotWh, total_wh, sk.UnitSymbolKind_Wh, now)
        set_bcr(mmtr.TotVArh, 0, sk.UnitSymbolKind_VArh, now)
        set_bcr(mmtr.TotVAh, total_wh, sk.UnitSymbolKind_VAh, now)

        return mmtr

    def update_mmtr(self, now):
        """Update the present net energy values."""
        duration = (now - self.last_update).total_seconds()

        net = self.w * duration / 3600.0
        if net > 0:
            self.dmd_wh += net
        else:
            self.sup_wh += net

        self.last_update = now

    @property
    def i_mag(self):
        """Get the magnitude of the current."""
        return self.w / self.ph_v if self.ph_v != 0 else 0

    @property
    def va(self):
        """Get the complex power output."""
        return abs(self.w)

    @property
    def w(self):
        """Get the real power output."""
        return self._w

    @w.setter
    def w(self, value):
        """Set the real power set-point."""
        with self.lock:
            self.update_mmtr(datetime.utcnow())
            self._w = value
