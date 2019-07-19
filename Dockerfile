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

FROM python:3.7-alpine
WORKDIR /app

COPY ./deps/. ./deps/
COPY ./openfmbsim/. ./openfmbsim/
COPY ./tests/. ./tests/
COPY ./requirements-dev.txt ./

RUN echo "Installing required Python dependencies" \
&& pip install -r requirements-dev.txt \
&& echo "Running tests in the container environment" \
&& pytest tests \
&& echo "Cleaning up tests from the container environment" \
&& rm -r /app/tests

# Expose required ports
EXPOSE 5000

# Define the application to run when the image starts
ENTRYPOINT ["python", "-m", "openfmbsim.server"]
CMD []
