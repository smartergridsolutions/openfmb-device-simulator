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
"""Tests of the simulated single phase solar module."""

from uuid import UUID
from openfmbsim.devices.single_phase_solar import SinglePhaseSolar


def test_device_mrid_automatically_creates():
    spb = SinglePhaseSolar()

    assert spb.device_mrid is not None


def test_to_profiles():
    uuid_val = "12345678-1234-5678-1234-567812345678"
    sph = SinglePhaseSolar(UUID(uuid_val))
    profiles = list(sph.to_profiles())

    assert len(profiles) == 2
    assert profiles[0].solarInverter.conductingEquipment.mRID == uuid_val


def test_to_reading_when_not_set_power():
    sph = SinglePhaseSolar()
    gm = sph.to_reading()

    assert gm.readingMMXU.W.phsA.cVal.mag.f.value == 1000000


def test_to_reading_when_power_is_set():
    sph = SinglePhaseSolar()
    sph.w = 2000
    gm = sph.to_reading()

    assert gm.readingMMXU.W.phsA.cVal.mag.f.value == 2000


def test_to_reading_when_power_is_set_neg():
    sph = SinglePhaseSolar()
    sph.w = -2000
    gm = sph.to_reading()

    assert gm.readingMMXU.W.phsA.cVal.mag.f.value == -2000
