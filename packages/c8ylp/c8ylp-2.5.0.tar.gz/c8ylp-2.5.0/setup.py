#
# Copyright (c) 2021 Software AG, Darmstadt, Germany and/or its licensors
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from setuptools import setup, find_packages
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    python_requires=">=3.7",
    name="c8ylp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="Cumulocity Local Client Proxy",
    author="Stefan Witschel",
    author_email="Stefan.Witschel@softwareag.com",
    url="https://github.com/SoftwareAG/cumulocity-remote-access-local-proxy",
    license="Apache v2",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["c8ylp=c8ylp.main:cli"],
    },
    install_requires=[
        "requests>=2.26.0",
        "websocket_client>=1.2.1",
        "certifi>=2020.12.5",
        "click==8.1.7",
    ],
    zip_safe=False,
)
