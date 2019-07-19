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
"""The primary server that sends and receives messages."""

import argparse
import asyncio
import logging
import os
import sys
from openfmbsim.nats_server import create_server
from openfmbsim.web_server import create_web_server
from openfmbsim.simulated_system import SimulatedSystem

LOGGER = logging.getLogger(__name__)


def listen_url(arg):
    fragments = arg.split(":")
    if len(fragments) != 2:
        raise argparse.ArgumentTypeError
    try:
        port = int(fragments[1])
    except ValueError:
        raise argparse.ArgumentTypeError
    return (fragments[0], port)


def parse_arguments(cmd_line):
    """Parse command line arguments into the args structure.

    :param cmd_line: Array of command line arguments.
    :return: The arguments structure.
    """
    env = os.environ
    parser = argparse.ArgumentParser(description="An OpenFMB device simulator")
    parser.add_argument("--servers",
                        action="append",
                        default=[],
                        help=("A server to connect to, for example "
                              "'nats://localhost:4222'."))
    parser.add_argument("--verbose",
                        action="store_true",
                        default=env.get("ODS_VERBOSE", False),
                        help="Enable verbose logging.")
    parser.add_argument("--listen",
                        default=env.get("ODS_LISTEN", "0.0.0.0:5000"),
                        type=listen_url,
                        help="The server and port that the web service listens"
                             " on.")
    args = parser.parse_args(cmd_line)

    if len(args.servers) == 0:
        args.servers = list(filter(None,
                                   env.get("ODS_SERVERS", "").split(";")))
    if len(args.servers) == 0:
        args.servers.append("nats://localhost:4222")

    return args


def main(cmd_line):
    """Entry point for the application.

    :param cmd_line: Array of command line arguments (without the application
                     name).
    """
    args = parse_arguments(cmd_line)
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    event_loop = asyncio.get_event_loop()

    system = SimulatedSystem()

    # The web server really wants to own the event loop, so we first
    # create the NATS server.
    nats_disposable = create_server(args.servers, system, event_loop)

    try:
        # Start the web server to visualize the system in an alternative way
        # The web server handles the termination detection
        # The server will initialize the system before it starts
        create_web_server(args.listen[0], args.listen[1], event_loop, system)
    finally:
        nats_disposable()
        event_loop.run_until_complete(event_loop.shutdown_asyncgens())
        event_loop.close()


if __name__ == '__main__':
    main(sys.argv[1:])
