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
"""Common utilities for writing into protobuf structures."""

from datetime import datetime
import commonmodule_pb2 as cm


def write_timestamp(ts, now: datetime):
    """Set fields for the given TimeStamp structure based on current time."""
    fractional_seconds = now.timestamp()
    seconds = int(fractional_seconds)
    ts.fraction = int((fractional_seconds - seconds) * 4294967295)
    ts.seconds = seconds
    ts.tq.clockFailure = False
    ts.tq.clockNotSynchronized = False
    ts.tq.leapSecondsKnown = True

    ts.tq.timeAccuracy = cm.TimeAccuracyKind.TimeAccuracyKind_unspecified
