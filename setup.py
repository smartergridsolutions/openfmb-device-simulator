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
"""Build and install the OpenFMB device simulator."""

from setuptools import setup
import os

_here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

version = {}
with open(os.path.join(_here, 'openfmbsim', 'version.py')) as f:
    exec(f.read(), version)

dependencies = []
with open(os.path.join(_here, 'requirements.txt')) as f:
    dependencies = [line.strip() for line in f.readlines()]

setup(
    name='smartergridsolutions.openfmb_device_simulator',
    version=version['__version__'],
    description=('A device simulator that published OpenFMB messages.'),
    long_description=long_description,
    author='Smarter Grid Solutions',
    author_email='gfick@smartergridsolutions.com',
    url='https://github.com/smartergridsolutions/openfmb-device-simulator',
    license='Apache License 2.0',
    packages=['openfmbsim'],
    install_requires=dependencies,
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: Apache Software License']
    )
