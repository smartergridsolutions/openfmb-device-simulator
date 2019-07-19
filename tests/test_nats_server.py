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
"""Tests of the nats server module."""

import asyncio
import collections
import pytest
import socket
from contextlib import closing
from openfmbsim.nats_server import create_server, NatsSubscriber, NatsPublisher
from openfmbsim.simulated_system import SimulatedSystem
import generationmodule_pb2 as gm


class MockNats():
    """A mocked NATS client so we can test without a connection."""

    async def connect(self, servers, loop):
        """Connect to the server."""
        return asyncio.Future()

    async def subscribe(self, subject, cb):
        """Subscribe to the subject."""
        return asyncio.Future()

    async def close(self):
        """Close the connection."""
        return asyncio.Future()


def is_nats_available():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex(("127.0.0.1", 4222)) == 0
    return False


@pytest.mark.skipif(not is_nats_available(),
                    reason="NATS is not running locally")
def test_integration_create_server_returns_canceler():
    event_loop = asyncio.new_event_loop()
    system = SimulatedSystem()
    canceler = create_server(servers=["nats://127.0.0.1:4222"], system=system,
                             event_loop=event_loop)

    canceler()


def test_create_server_returns_canceler():
    event_loop = asyncio.new_event_loop()
    system = SimulatedSystem()
    canceler = create_server(servers=["nats://127.0.0.1:4222"], system=system,
                             event_loop=event_loop, nats=MockNats())

    canceler()


@pytest.mark.asyncio
async def test_nats_subscriber_event_handler():
    system = SimulatedSystem()
    event_loop = asyncio.new_event_loop()
    mock_nats = MockNats()
    subscriber = NatsSubscriber([], system, event_loop, mock_nats)

    await subscriber.start()

    # Send an event
    model = gm.GenerationReadingProfile
    encoded_model = model().SerializeToString()
    Message = collections.namedtuple("Message", "data subject")
    msg = Message(data=encoded_model, subject="")

    await subscriber.event_handler(model, msg)


@pytest.mark.asyncio
async def test_nats_subscriber_event_handler_invalid_data():
    system = SimulatedSystem()
    event_loop = asyncio.new_event_loop()
    mock_nats = MockNats()
    subscriber = NatsSubscriber([], system, event_loop, mock_nats)

    await subscriber.start()

    # Send an event
    model = gm.GenerationReadingProfile
    Message = collections.namedtuple("Message", "data subject")
    msg = Message(data="", subject="")

    # We don't have much to test other than we didn't raise
    await subscriber.event_handler(model, msg)


@pytest.mark.asyncio
async def test_nats_publisher_publish():
    system = SimulatedSystem()
    loop = asyncio.get_event_loop()
    mock_nats = MockNats()
    publisher = NatsPublisher([], system, loop, mock_nats)

    await publisher.start()

    profile = gm.GenerationReadingProfile()
    publisher.publish_async(profile)
