
# Releases

## 2.3.0

* feat #81: Support stdin/out forwarding to the Cumulocity server it can be used directly as a ssh ProxyCommand without the need of starting a local TCP server and using socat. This method works for both, windows and unix.

    **Example**

    ```sh
    ssh -o 'ProxyCommand=c8ylp server <device> --stdio --env-file .env' <device_username>@<device>
    ```

    By adding the proxy command to the `.ssh/config` file, the usage of the Cumulocity server can be simplified even more.

    The file allows to define user and environment file so the connection can be done by simply typing `ssh <device>`.

    For this use the following example configuration (`%n` will be replaced by `ssh` with the given device name):

    ```sh
    Host <device>
        User <device_username>
        PreferredAuthentications publickey
        IdentityFile <identify_file>
        ServerAliveInterval 120
        StrictHostKeyChecking no
        UserKnownHostsFile /dev/null
        ProxyCommand c8ylp server %n --stdio --env-file .env
    
    # Or you can create a generic ssh config for all devices with a similar prefix:
    # Usage;
    #   => ssh linux-device01
    #   => ssh linux-device02
    Host linux-*
        User admin
        PreferredAuthentications publickey
        IdentityFile ~/.ssh/myprivatekey
        ServerAliveInterval 120
        StrictHostKeyChecking no
        UserKnownHostsFile /dev/null
        ProxyCommand c8ylp server %n --stdio --env-file .env
    ```

* chore: improve integration test compatibility to make it possible to run on MacOS. #85
* chore: upgrade dependencies. #78, #82, #84, #87

## 2.2.0

* feat: Unix only - Support starting a proxy using a Unix socket server (instead of a local tcp server).

    **Example**

    ```sh
    # Start c8ylp proxy server which uses a unix socket instead of a tcp server
    c8ylp server <device> --env-file .env --socket-path /tmp/device.socket

    # Use ssh with proxy command (requires socat)
    ssh -o 'ProxyCommand=socat - UNIX-CLIENT:/tmp/device.socket' <device_username>@localhost
    ```

* chore: update project dependencies

## 2.1.4

* `c8y connect ssh` supports reading the `--ssh-user` from the `C8YLP_SSH_USER` environment variable 

## 2.1.3

* Remove duplicated `-t` shorthand option for the `--token` option. Fixes #45
* Add new option to disable storage of token in an dotenv file using `--no-store-token` (opposite of the existing `--store-token` option)


## 2.1.2

* fix: Only display deprecation warning for `reconnects` option when it is used.

## 2.1.1

* fix: Added deprecation mark on `reconnects` option which was removed during an erroneous merge

## 2.1.0

* fix: Shutdown websocket when the tcp client terminates. #38
* fix: Mark `--reconnects` option as deprecated, it will be removed in the next major release. The reconnect logic websocket has been removed as attempting a reconnect after the client has been connected once causes problems with different servers. #40
* build: update dev dependencies

## 2.0.4

* fix: Tenant id detection works as expected even when SSO is enabled on a tenant is appears before the INTERNAL_OAUTH2 option in /tenant/loginOptions.

## 2.0.3

* fix: The Cumulocity host is now normalized by trimming whitespace and trailing forward slashes

## 2.0.2

* fix: `c8ylp login --help` no longer prompts the user for the host when trying to display the help
* ci: Trigger GitHub publish action when a GitHub Release has been set to publish or it is manually triggered

## 2.0.1

### Breaking changes

* Renamed command structure and parameter names. Checkout the [migration notes](docs/MIGRATION_V2.md) for full details to get the most out of the newer version.

* Restructured project and dependencies
    * Add code formatting and linting
    * Refactor code to simplify interactions between the local tcp server and the websocket client
    * Add unit and integration tests (coverage currently around ~85%)

* Enabled calling project using just the module name, i.e. `python3 -m c8ylp.main` => `python3 -m c8ylp`

* Added repo hosted cli [documentation](docs/cli/C8YLP.md)

* A PID file is no longer created when using server mode `c8ylp server`. This feature has been removed from c8ylp. It is now recommended that users use the `c8ylp connect ssh` or `c8ylp plugin command` which will automatically shutdown the local proxy after the user is finished with it.

### Features

* Load configuration from an environment via the `--env-file` parameter and support caching the Cumulocity token to it.

* Support usage of random port when starting the local proxy via `--port 0`

* Add interactive ssh connection which starts a once-off local proxy on a random port and then starts an SSH client automatically. Once the ssh client disconnects the local proxy is shutdown.

* [c8ylp plugin command](docs/cli/C8YLP_PLUGIN_COMMAND.md) Generic subcommand to execute custom commands to launch ssh yourself (instead of via `c8ylp connect ssh`). This allows you to customize your ssh options.

* Plugin support to allow the user to extend c8ylp functionality by use of external plugins in the form of python or shell scripts. See [docs/PLUGINS](docs/PLUGINS.md) for information

* Support multiple environment variables for setting Cumulocity credentials to improve compatibility with other Cumulocity tooling

### Bug fixes

* Port timeout error when running on windows

* Fixed randomized port race condition by letting the operating system assign a random port when starting the local tcp server
