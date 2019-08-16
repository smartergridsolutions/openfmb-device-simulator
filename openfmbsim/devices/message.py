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

import commonmodule_pb2 as cm
from datetime import datetime
from ..message import write_timestamp


def set_phase_a_mmxu(mmxu, mmxu_dict: dict, now: datetime):
    """Set the values in the MMXU structure.

    :param mmxu: The MMXU structure to populate.
    :param mmxu_dict: Dict of MMXU values.
    :param now: The timestamp for the value.
    """
    sk = cm.UnitSymbolKind
    set_cmvs([mmxu.A.phsA, mmxu.A.net], mmxu_dict["A"], 0,
             sk.UnitSymbolKind_Amp, now)

    mmxu.Hz.mag.f.value = mmxu_dict["Hz"]
    mmxu.Hz.units.SIUnit = sk.UnitSymbolKind_Hz

    set_cmvs([mmxu.PF.phsA, mmxu.PF.net], mmxu_dict["PF"], 0,
             sk.UnitSymbolKind_none, now)

    mmxu.PFSign.setVal = mmxu_dict["PFSign"]

    set_cmvs([mmxu.PhV.phsA, mmxu.PhV.net], mmxu_dict["V"], 0,
             sk.UnitSymbolKind_V, now)
    set_cmvs([mmxu.VA.phsA, mmxu.VA.net], mmxu_dict["VA"], 0,
             sk.UnitSymbolKind_VA, now)
    set_cmvs([mmxu.VAr.phsA, mmxu.VAr.net], mmxu_dict["VAr"], 0,
             sk.UnitSymbolKind_VAr, now)
    set_cmvs([mmxu.W.phsA, mmxu.W.net], mmxu_dict["W"], 0,
             sk.UnitSymbolKind_W, now)


def set_cmvs(cmvs, mag, ang, unit, now: datetime):
    """Set the values in the specified CMV structures.

    :param mag: The value's magnitude.
    :param ang: The value's angle.
    :param unit: The value's unit.
    :param now: The timestamp for the value.
    """
    for cmv in cmvs:
        cmv.cVal.mag.f.value = mag
        cmv.cVal.ang.f.value = ang
        cmv.units.SIUnit = unit
        write_timestamp(cmv.t, now)


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
