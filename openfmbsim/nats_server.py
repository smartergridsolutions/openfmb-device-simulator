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
"""Message handler that subscribes and publishes on NATS."""

import asyncio
import functools
import logging
from nats.aio.client import Client as Nats
import reclosermodule_pb2 as rm
import generationmodule_pb2 as gm

LOGGER = logging.getLogger(__name__)

# The types from protobuf that we subscribe to.
SUBSCRIBE_PROFILES_TYPES = [
    rm.RecloserControlProfile,
    gm.GenerationControlProfile
]


def profile_to_subject(device_mrid, profile):
    """Convert the profile to it's topic as per RMQ.26.6.5.2.

    :param device_mrid: The MRID of the device.
    :param profile: The protobuf profile object.
    """
    return ".".join(["openfmb", profile.DESCRIPTOR.full_name, device_mrid])


class NatsSubscriber():
    """Subscriber for messages coming over NATS for devices in the system."""

    def __init__(self, servers, system, event_loop, nats=None):
        """Initialize the subscriber.

        :param subject: NATS subject name to subscribe to.
        :param servers: List of server URIs for connection.
        :param system: The system that we are simulating.
        :param event_loop: The event loop for the asyncio.
        :param nats: If not none, use as the NATS client.
        :type servers: array of str
        """
        LOGGER.info("Starting NATS subscriber on %s", servers)
        self.nc = Nats() if nats is None else nats
        self.servers = servers
        self.system = system
        self.event_loop = event_loop

    async def event_handler(self, model, msg):
        """Handle messages received from NATS.

        :param model: Constructor for the protobuf object to decode the data
        :param msg: The message received from NATS.
        """
        try:
            msg_data = msg.data
            LOGGER.info("[Received '%s' on '%s']: %s", model, msg.subject,
                        msg_data)

            profile = model()
            profile.ParseFromString(msg_data)

            # The last part of the subject is the MRID of the conducting
            # equipment, so extract that value.
            device_mrid = msg.subject.split(".")[-1]

            LOGGER.debug("[Decoded profile '%s']: %s", msg.subject, profile)

            self.system.update_profile(device_mrid, profile)
        except TypeError:
            LOGGER.exception("Error encountered")

    async def start(self):
        """Start the subscriber by connecting to the cluster."""
        await self.nc.connect(servers=self.servers, loop=self.event_loop)
        for profile in SUBSCRIBE_PROFILES_TYPES:
            subject = profile_to_subject("*", profile)
            callback = functools.partial(self.event_handler, profile)
            await self.nc.subscribe(subject, cb=callback)


class NatsPublisher():
    """Publisher to send information over NATS about devices in the system."""

    def __init__(self, servers, system, event_loop, nats=None):
        """Initialize the publisher.

        :param servers: List of server URIs for connection.
        :param system: The system that we are simulating. We subscribe to
                       the stream from that system.
        :param event_loop: The event loop for the asyncio.
        :param nats: If not none, use as the NATS client.
        """
        LOGGER.info("Starting NATS publisher on %s", servers)
        self.nc = Nats() if nats is None else nats
        self.servers = servers
        self.system = system
        self.event_loop = event_loop

        # Subscribe to the stream of published profiles
        def publish(profiles):
            self.publish_async(profiles)
        self.system.subscribe(publish)

    async def start(self):
        """Start the publisher."""
        await self.nc.connect(servers=self.servers, loop=self.event_loop)

    def publish_async(self, profile):
        """Handle subscriptions from the observable to send to the event loop.

        This bridges the reactive and async worlds in this application.
        """
        def callback():
            asyncio.ensure_future(self.publish(profile[0], profile[2]))
        asyncio.get_event_loop().call_soon(callback)

    @asyncio.coroutine
    def publish(self, device_mrid, profile):
        """Publish called from the asyncio thread to publish profiles.

        :param device_mrid: The MRID of the associated device.
        :param profile: The profile encoded as an OpenFMB protobuf object.
        """
        subject = profile_to_subject(str(device_mrid), profile)
        yield from self.nc.publish(subject, profile.SerializeToString())


def create_server(servers, system, event_loop, nats=None):
    """Create a NATS server for the system.

    Starts the system, will do nothing until the event loop is set running.

    :param servers: List of NATS servers to connect to
    :param system: The system that contains the nodes, publishes information.
    :param event_loop: The event loop for the asyncio.
    :param nats: If not none, use as the NATS client.
    :return: A function to shutdown the server.
    """
    subscriber = NatsSubscriber(servers=servers, system=system,
                                event_loop=event_loop, nats=nats)
    event_loop.run_until_complete(subscriber.start())

    publisher = NatsPublisher(servers=servers, system=system,
                              event_loop=event_loop, nats=nats)
    event_loop.run_until_complete(publisher.start())

    def canceler():
        system.dispose()
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(subscriber.nc.close())
        event_loop.create_task(publisher.nc.close())

    return canceler
