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
"""Test plugin command"""

import os
import shutil
import subprocess
import sys

import pytest

from .fixtures import Device


def proxy_cli(*args, **kwargs) -> subprocess.CompletedProcess:
    """Execute the proxy cli command with given arguments"""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "c8ylp",
            *args,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs,
    )


def stdio_cli(*args, **kwargs) -> subprocess.CompletedProcess:
    """Execute the proxy cli command using stdin/out forwarding"""
    if not shutil.which("ssh"):
        pytest.fail(
            "ssh client not found. Please make sure the 'ssh' client is included in your PATH variable"
        )

    return subprocess.run(
        [
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            f"ProxyCommand={sys.executable} -m c8ylp server %n --stdio --env-file .env",
            *args,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs,
    )


@pytest.mark.parametrize(
    "case",
    (
        dict(command="sleep 1", exit_code=0),
        dict(command="sleep 1; exit 111", exit_code=111),
        dict(command="sleep 1; exit 111", user="unknown_user", exit_code=255),
    ),
    ids=lambda x: str(x),
)
def test_stdio_ssh_command_then_exit(case, c8ydevice: Device):
    """Test running a once off ssh command"""
    user = case.get("user", c8ydevice.ssh_user)
    command = case.get("command", "sleep 10")

    result = stdio_cli(
        f"{user}@{c8ydevice.device}",
        command,
    )

    assert result.returncode == case.get("exit_code", 0)


@pytest.mark.parametrize(
    "case",
    (
        dict(command="sleep 1", exit_code=0),
        dict(command="sleep 1; exit 111", exit_code=111),
        dict(command="sleep 1; exit 111", user="unknown_user", exit_code=255),
    ),
    ids=lambda x: str(x),
)
def test_ssh_command_then_exit(case, c8ydevice: Device):
    """Test running a once off ssh command"""
    user = case.get("user", c8ydevice.ssh_user)
    command = case.get("command", "sleep 10")

    result = proxy_cli(
        "connect",
        "ssh",
        c8ydevice.device,
        "--ssh-user",
        user,
        "--",
        command,
    )

    assert result.returncode == case.get("exit_code", 0)


@pytest.mark.parametrize(
    "case",
    (dict(command="sleep 1", exit_code=0),),
    ids=lambda x: str(x),
)
def test_support_ssh_user_via_env(case, c8ydevice: Device):
    """Test ssh command should support setting the ssh user via env variable"""
    user = case.get("user", c8ydevice.ssh_user)
    command = case.get("command", "sleep 10")

    result = proxy_cli(
        "connect",
        "ssh",
        c8ydevice.device,
        "--",
        command,
        env={
            **os.environ,
            "C8YLP_SSH_USER": user,
        },
    )

    assert result.returncode == case.get("exit_code", 0)
