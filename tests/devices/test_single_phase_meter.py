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
"""Tests of the simulated single phase battery module."""

from uuid import UUID
from openfmbsim.devices.single_phase_meter import SinglePhaseMeter


def test_device_mrid_automatically_creates():
    sph = SinglePhaseMeter()

    assert sph.device_mrid is not None


def test_to_profiles():
    uuid_val = "12345678-1234-5678-1234-567812345678"
    sph = SinglePhaseMeter(UUID(uuid_val))
    profiles = list(sph.to_profiles())

    assert len(profiles) == 1
    assert profiles[0].meter.conductingEquipment.mRID == uuid_val


def test_to_meter_reading_when_not_set_power():
    sph = SinglePhaseMeter()
    gm = sph.to_meter_reading()

    assert gm.readingMMXU.W.phsA.cVal.mag.f.value == 1000000


def test_to_meter_reading_when_power_is_set():
    sph = SinglePhaseMeter()
    sph.w = 2000
    gm = sph.to_meter_reading()

    assert gm.readingMMXU.W.phsA.cVal.mag.f.value == 2000


def test_to_meter_reading_when_power_is_set_neg():
    sph = SinglePhaseMeter()
    sph.w = -2000
    gm = sph.to_meter_reading()

    assert gm.readingMMXU.W.phsA.cVal.mag.f.value == -2000
