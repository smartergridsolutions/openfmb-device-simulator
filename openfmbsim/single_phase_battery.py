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
import commonmodule_pb2 as cm
import generationmodule_pb2 as gm


class SinglePhaseRealOnlyBattery(object):
    """A simulated single phase battery.

    This is intended to simulate a battery that might be installed in a split
    phase scenario. This is just to keep things simple for the purposes of
    development and integration.

    This also only accounts for real power - you can thus think of this as a
    very simple battery.
    """

    def __init__(self):
        """Construct a new instance of this battery model."""
        self.ph_v = 120
        self._w = 1000000
        self.hz = 60

        self.last_update = datetime.utcnow()
        self.dmd_wh = 0
        self.sup_wh = 0

        self.lock = threading.Lock()

    def to_profiles(self):
        """Get all of the profiles that this generates."""
        gp = gm.GenerationReadingProfile()
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
        mmxu.A.phsA.cVal.mag.f.value = self.i_mag
        mmxu.A.phsA.cVal.ang.f.value = 0
        mmxu.A.phsA.units.SIUnit = cm.UnitSymbolKind.UnitSymbolKind_Amp

        mmxu.Hz.mag.f.value = self.hz
        mmxu.Hz.units.SIUnit = cm.UnitSymbolKind.UnitSymbolKind_Hz

        mmxu.PF.phsA.cVal.mag.f.value = 1
        mmxu.PF.phsA.cVal.ang.f.value = 0
        mmxu.PF.phsA.units.SIUnit = cm.UnitSymbolKind.UnitSymbolKind_none

        mmxu.PFSign.setVal = 0

        mmxu.PhV.phsA.cVal.mag.f.value = self.ph_v
        mmxu.PhV.phsA.cVal.ang.f.value = 0
        mmxu.PhV.phsA.units.SIUnit = cm.UnitSymbolKind.UnitSymbolKind_V

        mmxu.VA.phsA.cVal.mag.f.value = self.va
        mmxu.VA.phsA.cVal.ang.f.value = 0
        mmxu.VA.phsA.units.SIUnit = cm.UnitSymbolKind.UnitSymbolKind_VA

        mmxu.VAr.phsA.cVal.mag.f.value = 0
        mmxu.VAr.phsA.cVal.ang.f.value = 0
        mmxu.VAr.phsA.units.SIUnit = cm.UnitSymbolKind.UnitSymbolKind_VAr

        mmxu.W.phsA.cVal.mag.f.value = self.w
        mmxu.W.phsA.cVal.ang.f.value = 0
        mmxu.W.phsA.units.SIUnit = cm.UnitSymbolKind.UnitSymbolKind_W

    def to_mmtr(self, mmtr):
        """Write the MMTR data into the specified structure."""
        mmtr.DmdWh.actVal = int(self.dmd_wh)
        mmtr.DmdWh.units.value = cm.UnitSymbolKind.UnitSymbolKind_Wh
        mmtr.DmdVArh.actVal = 0
        mmtr.DmdVArh.units.value = cm.UnitSymbolKind.UnitSymbolKind_VArh
        mmtr.DmdVAh.actVal = int(self.dmd_wh)
        mmtr.DmdVAh.units.value = cm.UnitSymbolKind.UnitSymbolKind_VAh

        mmtr.SupWh.actVal = int(self.sup_wh)
        mmtr.SupWh.units.value = cm.UnitSymbolKind.UnitSymbolKind_Wh
        mmtr.SupVArh.actVal = 0
        mmtr.SupVArh.units.value = cm.UnitSymbolKind.UnitSymbolKind_VArh
        mmtr.SupVAh.actVal = int(self.sup_wh)
        mmtr.SupVAh.units.value = cm.UnitSymbolKind.UnitSymbolKind_VAh

        total_wh = int(self.sup_wh - self.dmd_wh)
        mmtr.TotWh.actVal = total_wh
        mmtr.TotWh.units.value = cm.UnitSymbolKind.UnitSymbolKind_Wh
        mmtr.TotVArh.actVal = 0
        mmtr.TotVArh.units.value = cm.UnitSymbolKind.UnitSymbolKind_VArh
        mmtr.TotVAh.actVal = total_wh
        mmtr.TotVAh.units.value = cm.UnitSymbolKind.UnitSymbolKind_VAh

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
