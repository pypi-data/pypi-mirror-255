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
"""SSH command tests"""
import pytest
import responses
from click.testing import CliRunner
from c8ylp.main import cli
from tests.env import Environment
from tests.fixtures import FixtureCumulocityAPI


@pytest.mark.parametrize(
    "inputs",
    (
        {
            "stdin": [
                "https://example.c8y.io\n",
                "example-user\n",
                "dummy-password\n",
                "12345\n",
            ],
            "env": {},
        },
        {
            # Include trailing slash
            "stdin": [
                "https://example.c8y.io/\n",
                "example-user\n",
                "dummy-password\n",
                "12345\n",
            ],
            "env": {},
        },
        {
            "stdin": [
                "https://example.c8y.io\n",
                "dummy-password\n",
                "12345\n",
            ],
            "env": {
                "C8Y_USER": "example-user",
            },
        },
        {
            "stdin": [
                "https://example.c8y.io\n",
                "12345\n",
            ],
            "env": {
                "C8Y_USER": "example-user",
                "C8Y_PASSWORD": "example-user",
            },
        },
        {
            "stdin": [
                "12345\n",
            ],
            "env": {
                "C8Y_USER": "example-user",
                "C8Y_PASSWORD": "example-user",
                "C8Y_HOST": "https://example.c8y.io",
            },
        },
    ),
)
def test_prompt_for_details(
    inputs, c8yserver: FixtureCumulocityAPI, env: Environment, tmpdir
):
    """Ask user for missing parameters"""

    @responses.activate
    def run():
        c8yserver.simulate_loginoptions()
        c8yserver.simulate_login_oauth(status_codes=[401, 200])

        env_file = tmpdir.join(".env")
        stdin = "".join(inputs["stdin"])

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["login", "--env-file", env_file.strpath],
            env={
                **env.create_empty_env(),
                **inputs["env"],
            },
            input=stdin,
        )

        assert result.exit_code == 0

        settings = env.read_file(env_file)
        assert settings == {
            "C8Y_HOST": "https://example.c8y.io",
            "C8Y_USER": "example-user",
            "C8Y_TENANT": "t12345",
            "C8Y_TOKEN": "dummy-token-xyz",
        }

    run()


def test_repeated_login_failures(c8yserver: FixtureCumulocityAPI, env: Environment):
    """Test repeated login failures. Eventually c8ylp should give up"""

    @responses.activate
    def run():
        c8yserver.simulate_loginoptions()
        c8yserver.simulate_login_oauth(status_codes=[401, 401, 401, 401])

        stdin = "".join(
            [
                "password\n",
                "tfa\n",
                "password\n",
                "tfa\n",
            ]
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["login", "--host", c8yserver.base_url, "--user", "dummy_user"],
            env={
                **env.create_empty_env(),
            },
            input=stdin,
        )

        assert result.exit_code == 2

    run()


def test_disable_prompts(c8yserver: FixtureCumulocityAPI, env: Environment):
    """Test disabling of prompts for usage in scripts"""

    @responses.activate
    def run():
        c8yserver.simulate_loginoptions()
        c8yserver.simulate_login_oauth(status_codes=[401, 401, 401, 401])

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "login",
                "--host",
                c8yserver.base_url,
                "--user",
                "dummy_user",
                "--disable-prompts",
            ],
            env={
                **env.create_empty_env(),
            },
        )

        assert result.exit_code == 2

    run()


def test_help_without_host(env: Environment):
    """Test display of help with providing any other options"""

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "login",
            "--help",
        ],
        env={
            **env.create_empty_env(),
        },
        # Use dummy stdin, so that in case the command does expect input
        # but it should not appear in the output
        input="dummyinput",
    )

    assert result.exit_code == 0
    assert "Host: " not in result.output, "User should not be prompted for hostname"
    assert "dummyinput" not in result.output, "User should not be prompted for hostname"


@pytest.mark.parametrize(
    "inputs",
    (
        {
            "stdin": [],
            "args": [
                "--host",
                "https://example.c8y.io",
                "-u",
                "myuser@company.com",
                "-p",
                "my-dummy45-password",
                "-t",
                "t12345",
                "--token",
                "98765",
            ],
            "env": {},
        },
    ),
)
def test_shorthand_login_options(
    inputs, c8yserver: FixtureCumulocityAPI, env: Environment, tmpdir
):
    """Test shorthand options when logging in"""

    @responses.activate
    def run():
        c8yserver.simulate_loginoptions()
        c8yserver.simulate_login_oauth(status_codes=[401, 200])
        c8yserver.simulate_current_user()

        env_file = tmpdir.join(".env")
        stdin = "".join(inputs["stdin"])

        args = ["login", "--env-file", env_file.strpath, *inputs["args"]]

        runner = CliRunner()
        result = runner.invoke(
            cli,
            args,
            env={
                **env.create_empty_env(),
                **inputs["env"],
            },
            input=stdin,
        )

        assert result.exit_code == 0

        settings = env.read_file(env_file)
        assert settings == {
            "C8Y_HOST": "https://example.c8y.io",
            "C8Y_USER": "myuser@company.com",
            "C8Y_TENANT": "t12345",
            "C8Y_TOKEN": "98765",
        }

    run()


@pytest.mark.parametrize(
    "inputs",
    (
        {
            # Default behaviour is to store the token to the given --env-file
            "stdin": [],
            "args": ["--token", "98765"],
            "env": {
                "C8Y_HOST": "https://example.c8y.io",
                "C8Y_USER": "myuser@company.com",
                "C8Y_TENANT": "t12345",
            },
            "expected_env": {
                "C8Y_HOST": "https://example.c8y.io",
                "C8Y_USER": "myuser@company.com",
                "C8Y_TENANT": "t12345",
                "C8Y_TOKEN": "98765",
            },
        },
        # User explicitly wants to store the token
        {
            "stdin": [],
            "args": ["--token", "98765", "--store-token"],
            "env": {
                "C8Y_HOST": "https://example.c8y.io",
                "C8Y_USER": "myuser@company.com",
                "C8Y_TENANT": "t12345",
            },
            "expected_env": {
                "C8Y_HOST": "https://example.c8y.io",
                "C8Y_USER": "myuser@company.com",
                "C8Y_TENANT": "t12345",
                "C8Y_TOKEN": "98765",
            },
        },
        # User explicitly does not want to store the token
        {
            "stdin": [],
            "args": ["--token", "98765", "--no-store-token"],
            "env": {
                "C8Y_HOST": "https://example.c8y.io",
                "C8Y_USER": "myuser@company.com",
                "C8Y_TENANT": "t12345",
            },
            "expected_env": {
                "C8Y_HOST": "https://example.c8y.io",
                "C8Y_USER": "myuser@company.com",
                "C8Y_TENANT": "t12345",
            },
        },
    ),
)
def test_disable_token_storage(
    inputs, c8yserver: FixtureCumulocityAPI, env: Environment, tmpdir
):
    """Test disabling of the token storage by excluding it from the environment file"""

    @responses.activate
    def run():
        c8yserver.simulate_loginoptions()
        c8yserver.simulate_login_oauth(status_codes=[401, 200])
        c8yserver.simulate_current_user()

        env_file = tmpdir.join(".env")

        # Seed the env file with some default values
        env_file.write_text(
            "\n".join([f"{key}={value}" for key, value in inputs["env"].items()]),
            "utf8",
        )

        stdin = "".join(inputs["stdin"])

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["login", "--env-file", env_file.strpath, *inputs["args"]],
            env={
                **env.create_empty_env(),
                **inputs["env"],
            },
            input=stdin,
        )

        assert result.exit_code == 0

        settings = env.read_file(env_file)
        assert settings == inputs["expected_env"]

    run()
