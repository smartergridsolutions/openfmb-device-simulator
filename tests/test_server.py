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
"""Tests of the server module."""

import os
import pytest
from openfmbsim.server import main, parse_arguments


def test_main_when_ihelp():
    with pytest.raises(SystemExit):
        main(["--help"])


def test_main_when_invalid_listen_host():
    with pytest.raises(SystemExit):
        main(["--listen", "not-a-uri"])


def test_main_when_invalid_listen_port():
    with pytest.raises(SystemExit):
        main(["--listen", "localhost:abc"])


def test_parse_arguments_when_env_set_listen():
    arg = os.environ.get("ODS_LISTEN", "")
    try:
        os.environ["ODS_LISTEN"] = "127.0.0.1:8080"
        args = parse_arguments([])
        assert args.listen == ("127.0.0.1", 8080)
    finally:
        os.environ["ODS_LISTEN"] = arg
