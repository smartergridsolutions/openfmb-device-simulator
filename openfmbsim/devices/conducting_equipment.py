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
"""Base class for all devices that provide readings."""

from datetime import datetime
import threading
from typing import Iterator
import uuid
from ..name_generator import make_random_name


class ConductingEquipment(object):
    """Defines a simple conducting equipment."""

    def __init__(self, cond_equipment_mrid: uuid.UUID = None,
                 cond_equipment_name: str = None):
        """Construct a new instance of this conducting equipment.

        :param cond_equipment_mrid: The MRID of the conducting unit.
        :param cond_equipment_name: The name of the conducting unit.
        """
        self.mrid = (cond_equipment_mrid
                     if cond_equipment_mrid is not None
                     else uuid.uuid4())

        self.name = (cond_equipment_name
                     if cond_equipment_name is not None
                     else make_random_name())

        self.last_update = datetime.utcnow()
        self.lock = threading.Lock()

    @property
    def device_mrid(self) -> uuid.UUID:
        """Get the ID of the underlying device."""
        return self.mrid

    def control_mrids(self) -> Iterator[uuid.UUID]:
        """Get the MRIDs of the controls in the simulated device."""
        return []
