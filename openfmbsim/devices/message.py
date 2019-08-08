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
"""Common utilities for writing messages."""

from datetime import datetime
from ..message import write_timestamp


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
