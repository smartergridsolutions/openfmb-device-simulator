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
"""Tests of the simulated system module."""

import uuid
from unittest.mock import Mock
from openfmbsim.simulated_system import SimulatedSystem
from openfmbsim.devices.single_phase_generator import SinglePhaseGenerator
import generationmodule_pb2 as gm


def test_remove_model_when_no_devices():
    system = SimulatedSystem()
    assert system.remove_model(uuid.uuid1()) is False


def test_remove_model_when_exists():
    system = SimulatedSystem()
    battery = SinglePhaseGenerator()
    uuid = system.add_model(battery)
    assert system.remove_model(uuid)

    assert len(system.devices) == 0
    assert len(system.subscriptions) == 0


def test_update_profile_when_mrid_doesnot_exist():
    # We have this to ensure that we are getting good test coverage.
    system = SimulatedSystem()

    profile = gm.GenerationControlProfile()
    system.update_profile("ae8b5a94-fa97-4140-96f1-1b2f6b9255f8", profile)


def test_update_profile_when_invalid_mrid():
    # We have this to ensure that we are getting good test coverage.
    system = SimulatedSystem()

    profile = gm.GenerationControlProfile()
    system.update_profile("ae8b5a94-fa97-4140-96f1", profile)


def test_update_profile_when_mrid_matches_device():
    # We have this to ensure that we are getting good test coverage.
    device_mrid = uuid.uuid4()
    battery = Mock(mrid=device_mrid)

    system = SimulatedSystem()
    system.add_model(battery)

    profile = gm.GenerationControlProfile()
    profile.generatingUnit.conductingEquipment.mRID = str(device_mrid)
    system.update_profile(str(device_mrid), profile)

    battery.update_profile.assert_called_once_with(profile)


def test_subscribe_returns_disposable():
    system = SimulatedSystem()

    # Adding a subscriber adds it to the list of subjects
    def subscriber(profile):
        pass
    disposable = system.subscribe(cb=subscriber)
    assert len(system.subjects) == 1

    # Disposing of it removes the item
    disposable()
    assert len(system.subjects) == 0
