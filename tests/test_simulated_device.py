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
"""Tests of the simulated device module."""

import datetime
import pytest
import rx
from openfmbsim.simulated_device import SimulatedDevice
from openfmbsim.devices.single_phase_generator import SinglePhaseGenerator
from openfmbsim.devices.single_phase_recloser import SinglePhaseRecloser
import commonmodule_pb2 as cm
import reclosermodule_pb2 as rm


@pytest.mark.asyncio
async def test_when_constructed_then_generates_update():
    model = SinglePhaseGenerator()
    dev = SimulatedDevice("ID", model)

    first = await rx.Observable.to_future((dev.observable.first()))

    assert len(first) == 3
    assert first[0] == "ID"
    assert isinstance(first[1], datetime.datetime)
    assert isinstance(first[2], object)

    dev.dispose()


@pytest.mark.asyncio
async def test_when_constructed_generates_periodic_events():
    model = SinglePhaseGenerator()
    dev = SimulatedDevice("ID", model)

    item = dev.observable.pairwise().first()
    first_two = await rx.Observable.to_future(item)

    assert len(first_two) == 2
    # Check that the dates are not the same and in the right order
    assert first_two[0][1] < first_two[1][1]

    dev.dispose()


def test_when_update_device_then_generates_status():
    device_mrid = "97aad232-578d-4223-b624-aba3298b239e"
    model = SinglePhaseRecloser()
    dev = SimulatedDevice(device_mrid, model)

    # Create the profile to open the recloser
    rp = rm.RecloserControlProfile()
    rp.recloser.conductingEquipment.mRID = device_mrid

    switch_pt = rp.recloserControl.recloserControlFSCC\
        .switchControlScheduleFSCH.ValDCSG.crvPts.add()
    switch_pt = cm.SwitchPoint()
    switch_pt.Pos.ctlVal = True

    # Now update the device with this control request
    dev.update_profile(rp)

    assert model.position == SinglePhaseRecloser.OPEN
