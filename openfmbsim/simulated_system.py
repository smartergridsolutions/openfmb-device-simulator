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
"""Aggregates all items in the system to provide a simple interface."""

import logging
import rx
import uuid
from openfmbsim.simulated_device import SimulatedDevice
import generationmodule_pb2 as gm


LOGGER = logging.getLogger(__name__)


class SimulatedSystem(object):
    """Container for multiple simulated items.

    This acts as a proxy to forward messages to the right simulation model
    and acts as a single publisher for all events.
    """

    def __init__(self):
        """Initialize the system."""
        self._devices = []
        self.subjects = []
        self.subscriptions = {}

    def dispose(self):
        """Stop the simulated system, shutting down all devices."""
        LOGGER.debug("Unsubscribing by system from models")
        for s in self.subscriptions.values():
            s.dispose()
        self.subscriptions = []

    def subscribe(self, cb):
        """Get an observable for changes published by devices in the system.

        :param cb: The subscription handler.
        :return: A function to dispose of the subscription.
        """
        subject = rx.subjects.Subject()
        disposable = subject.subscribe(cb)

        self.subjects.append(subject)

        def unsubscribe():
            disposable()
            self.subjects.remove(subject)

        return unsubscribe

    @property
    def devices(self):
        """Get the list of devices in the system."""
        return self._devices

    def add_model(self, model):
        """Add a new model into the system.

        :param model: The model to add into the system. This function
                      constructs the appropriate messaging scaffolding to
                      publish information from the model.

        :return: The UUID of the device.
        """
        ied_mrid = uuid.uuid4()
        device = SimulatedDevice(ied_mrid, model)

        def publish(profile):
            self.publish(profile)
        self.subscriptions[ied_mrid] = device.observable.subscribe(publish)

        self._devices.append(device)
        LOGGER.info("Added device %s - total number of devices %d",
                    device.id, len(self._devices))

        return ied_mrid

    def publish(self, profile):
        """Publish to profile to all subjects.

        :param profile: The profile to publish.
        """
        for subject in self.subjects:
            subject.on_next(profile)

    def remove_model(self, mrid):
        """Remove an existing model from the system.

        :param mrid: The MRID of the IED to remove.

        :return: True if a model was removed, otherwie false.
        """
        found = False
        device = next((d for d in self._devices if d.id == mrid), None)
        if device is not None:
            device.dispose()
            self._devices.remove(device)
            LOGGER.info("Removed device with ID %s", mrid)
            found = True
        else:
            LOGGER.warning("Unable to find device with ID %s", mrid)

        # Try to remove the subscription
        subscription = self.subscriptions.pop(mrid, None)
        if subscription is not None:
            subscription.dispose()
        else:
            LOGGER.warning("Unable to find subscriptioni with ID %s", mrid)

        return found

    def update_profile(self, profile):
        """Handle a control request encoded as a profile for a model.

        :param profile: The profile describing the control update.
        """
        if isinstance(profile, gm.GenerationControlProfile):
            mrid_str = profile.generatingUnit.conductingEquipment.mRID
        else:
            mrid_str = ""

        try:
            mrid = uuid.UUID(mrid_str)
        except ValueError:
            LOGGER.error("Profile MRID %s is not valid UUID.", mrid_str)
            return

        # Find the device that that mrid
        device = next((x for x in self._devices if x.device_mrid == mrid),
                      None)

        if device is not None:
            device.update_profile(profile)
        else:
            LOGGER.error("Device MRID %s does not exist.", mrid_str)
