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
import uuid
from .message import set_bcr, set_cmv
from .conducting_equipment import ConductingEquipment
import commonmodule_pb2 as cm
import generationmodule_pb2 as gm


class SinglePhaseGenerator(ConductingEquipment):
    """A simulated single phase battery.

    This is intended to simulate a battery that might be installed in a split
    phase scenario. This is just to keep things simple for the purposes of
    development and integration.

    This also only accounts for real power - you can thus think of this as a
    very simple battery.
    """

    def __init__(self, cond_equip_mrid: uuid.UUID = None,
                 cond_equip_name: str = None):
        """Construct a new instance of this meter model.

        :param cond_equip_mrid: The MRID of the conducting unit.
        :param cond_equip_name: The name of the conducting unit.
        """
        super().__init__(cond_equip_mrid, cond_equip_name)

        self.ph_v = 120
        self._w = 1000000
        self.hz = 60

        self.last_update = datetime.utcnow()
        self.dmd_wh = 0
        self.sup_wh = 0

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
