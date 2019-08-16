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
"""Wrapper for a simulated device to automatically publish information."""

import asyncio
from datetime import timedelta, datetime
import logging
import rx
import threading
import uuid
from .message import write_timestamp

LOGGER = logging.getLogger(__name__)


def write_message_info(message_info, uuid, now):
    """Write message info into the protobuf.

    :param message_info: The structure to write into.
    :param uuid: The UUID of the message.
    :param now: The datetime of the message. This is normally the same as the
                main message payload.
    """
    # For each message, there is a description of the message itself. Omit the
    # name and description since those are not meaningful for the message
    message_info.identifiedObject.mRID.value = str(uuid)
    write_timestamp(message_info.messageTimeStamp, now=now)


def write_ied_info(ied, uuid):
    """Write IED information into the protobuf.

    :param ied: The structure to write into.
    :param uuid: The UUID of the device.
    """
    ied.identifiedObject.mRID.value = str(uuid)


class SimulatedDevice(object):
    """Represents a device that periodically publishes profile information."""

    def __init__(self, ied_id: uuid.UUID, model,
                 rate: timedelta = timedelta(seconds=1)):
        """Create a new simulated device.

        :param ied_id: The MRID of the associated IED device.
        :param rate: The rate at which the device should publish updates.
        """
        self.id = ied_id
        self.subject = rx.subjects.Subject()
        self.event_loop = asyncio.get_event_loop()
        self.rate = rate
        self.model = model

        self.lock = threading.Lock()
        self.done = False

        # The last thing we do is start publishing
        self.event_loop.call_soon(self.publish_profiles, self)

    @property
    def observable(self) -> rx.Observable:
        """Get the observable for subscribing to updates."""
        return self.subject

    @staticmethod
    def publish_profiles(self):
        """Publish updates to the subject and requeue itself."""
        # This method is static so that it plays nicely with the event loop
        # If not, then the event loop cannot call this.
        LOGGER.debug("Publishing profiles for %s", self.id)

        for profile in self.model.to_profiles():
            now = datetime.utcnow()
            if hasattr(profile, "readingMessageInfo"):
                write_message_info(profile.readingMessageInfo.messageInfo,
                                   uuid.uuid4(),
                                   now)
                write_ied_info(profile.ied, self.id)

            self.subject.on_next((self.id,
                                  now,
                                  profile))

        with self.lock:
            if not self.done:
                # We always schedule at a first time in the future, and don't
                # consider if we are actually called on time. This helps us
                # degrade nicely by default if we are having trouble keeping up
                next_run = self.event_loop.time() + self.rate.total_seconds()
                self.event_loop.call_at(next_run, self.publish_profiles, self)

    def update_profile(self, profile):
        """Update this with the information from the control profile.

        :param profile: The control profile with the update.
        """
        self.model.update_profile(profile)

    def dispose(self):
        """Terminate the device so it stops publishing."""
        with self.lock:
            self.done = True

    @property
    def device_mrid(self) -> uuid.UUID:
        """Get the ID of the underlying device."""
        return self.model.mrid
