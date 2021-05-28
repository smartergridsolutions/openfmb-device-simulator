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
"""Tests of the web server module."""

import asyncio
import pytest
from openfmbsim.simulated_system import SimulatedSystem
from openfmbsim.web_server import app, publish_async, ServerSentEvent
import generationmodule_pb2 as gm


def test_server_send_event_encodes():
    event = ServerSentEvent('{\n"somejson":\n {\n}\n}\n')
    expected = b'data: {"somejson": {}}\r\n\r\n'
    assert expected == event.encode()


@pytest.fixture(name='test_app')
def _test_app(tmpdir):
    app.system = SimulatedSystem()
    return app


def test_publish_async(test_app):
    client_queue = asyncio.Queue()
    test_app.clients.add(client_queue)
    profile = gm.GenerationReadingProfile()
    publish_async((None, None, profile))
    assert client_queue.empty() is False


@pytest.mark.asyncio
async def test_index_returns_page(test_app):
    test_client = test_app.test_client()
    response = await test_client.get("/")
    assert response.status_code == 200
    body = await response.get_data(as_text=True)
    print(body)
    assert "<html>" in body


@pytest.mark.asyncio
async def test_create_returns_204(test_app):
    test_client = test_app.test_client()
    data = {"type": "generator"}
    response = await test_client.post("/devices", json=data)
    assert response.status_code == 204
    assert len(test_app.system.devices) == 1


@pytest.mark.asyncio
async def test_delete_when_doesnt_exist_returns_410(test_app):
    test_client = test_app.test_client()
    response = await test_client.delete(
        "/devices/329c465c-635c-4709-9912-89f1b2eaa22d"
    )
    assert response.status_code == 410


@pytest.mark.asyncio
async def test_delete_when_invalid_mrid_returns_400(test_app):
    test_client = test_app.test_client()
    response = await test_client.delete("/devices/not-a-mrid")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_sse_returns_stream(test_app):
    test_client = test_app.test_client()
    response = await test_client.get("/sse")
    assert response.status_code == 200
