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
"""Web server to visualize the devices and system information."""

import asyncio
import logging
import threading
import uuid
from google.protobuf.json_format import MessageToJson
from quart import Quart, render_template, make_response
from openfmbsim.single_phase_battery import SinglePhaseRealOnlyBattery

LOGGER = logging.getLogger(__name__)

app = Quart(__name__)
app.clients = set()
running = True

# A lock for accessing the list of clients that we send information to
lock = threading.Lock()


class ServerSentEvent:
    """Simple class that wraps up and encodes data in the SSE format."""

    def __init__(self, data: str):
        """Initialize a new instance of the event.

        :param data: The data to be encoded and sent. Newlines are replaced.
        """
        self.data = data

    def encode(self) -> bytes:
        """Encode this event as a byte array."""
        encoded = self.data.replace("\r", "").replace("\n", "")
        message = f"data: {encoded}"
        message = f"{message}\r\n\r\n"
        return message.encode('utf-8')


@app.route("/")
async def index():
    """Route handler for the index page."""
    return await render_template("index.html")


@app.route("/devices", methods=['POST'])
async def create():
    """Route handler to create a new device.

    We currently do not allow the caller to specify anything about the device.
    """
    LOGGER.info("Create a new device.")
    app.system.add_model(SinglePhaseRealOnlyBattery())
    return "Created", 204


@app.route("/devices/<mrid>", methods=['DELETE'])
async def delete(mrid):
    """Route handler to create a new device.

    We currently do not allow the caller to specify anything about the device.
    """
    LOGGER.info("Deleting device with mrid %s", mrid)
    try:
        mrid_obj = uuid.UUID(mrid)
    except ValueError:
        return ("Not MRID", 400)
    return ("OK", 200) if app.system.remove_model(mrid_obj) else ("Gone", 410)


@app.route('/sse')
async def sse():
    """Route handler for server sent events.

    This is how we stream data to the front end. This async function
    only returns when there is no more data or the client disconnects.
    """
    # We have just been called to create a new client, so lock the list.
    with lock:
        queue = asyncio.Queue()
        app.clients.add(queue)

    async def send_events():
        global running
        while running:
            try:
                data = await queue.get()
                event = ServerSentEvent(data)
                yield event.encode()
            except asyncio.CancelledError as ex:
                LOGGER.info("Sending events canceled")
                with lock:
                    app.clients.remove(queue)
                raise ex
            except ConnectionAbortedError:
                LOGGER.info("Connection aborted sending events")
                with lock:
                    app.clients.remove(queue)

    response = await make_response(
        send_events(),
        {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Transfer-Encoding': 'chunked',
        },
    )
    return response


def publish_async(profile):
    """Handle subscriptions from the observable to send to the event loop.

    This bridges the reactive and async worlds in this application.
    """
    with lock:
        for queue in app.clients:
            queue.put_nowait(MessageToJson(profile[2]))


@app.before_serving
def before_serving():
    """Create the system just before serving when everything is ready."""
    app.system.add_model(SinglePhaseRealOnlyBattery())


def create_web_server(host: str, port: int, loop, system):
    """Create and start an instance of the web server.

    :param host: The host to listen on, usually 'localhost'
    :param port: The port to listen on.
    :param system: The system to subscribe to for events.
    """
    LOGGER.info("Starting web server...")
    app.system = system
    system.subscribe(lambda profiles: publish_async(profiles))

    # This does not return until canceled
    app.run(host, port=port, loop=loop)

    LOGGER.info("Web server stopped - shutting down")

    global running
    running = False
