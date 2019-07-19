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
from openfmbsim.simulated_system import SimulatedSystem
from openfmbsim.single_phase_battery import SinglePhaseRealOnlyBattery


def test_remove_model_when_no_devices():
    system = SimulatedSystem()
    assert system.remove_model(uuid.uuid1()) is False


def test_remove_model_when_exists():
    system = SimulatedSystem()
    battery = SinglePhaseRealOnlyBattery()
    uuid = system.add_model(battery)
    assert system.remove_model(uuid)

    assert len(system.devices) == 0
    assert len(system.subscriptions) == 0


def test_update_profile_returns():
    # We have this to ensure that we are getting good test coverage.
    system = SimulatedSystem()
    system.update_profile(uuid.uuid1())
