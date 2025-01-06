
# WatchSync

WatchSync is a tool for synchronizing files when they are created or modified across different storage locations. A file can also be a local directory that, when detected as modified or created, is synchronized with the configured storage locations. A storage location can be a local or remote directory where a copy of the files will be sent.

The purpose of this tool is to have a backup of files in different storage locations to avoid losing important information. It is a file replication solution that is very easy to configure and use.

## Features

- Automatic synchronization of files and directories.
- Support for multiple local and remote storage locations.
- Easy to configure and use.
- Uses `rsync` for efficient file synchronization.

## Installation

### Requirements

WatchSync uses `rsync` for file synchronization, so it must be installed on the system. On Debian-based systems, it can be installed with the following command:

```bash
sudo apt install rsync
```

### As a package
Install the package with pip:
```bash
pip install watchsync
```

### From source code
Clone the repository:
```bash
git clone https://github.com/rlizana/watchsync.git
cd watchsync
```

Install dependencies and build the package:
```bash
poetry install
```

Install the package globally:
```bash
poetry build
pip install dist/watchsync-*.whl
```

## Usage

WatchSync uses a daemon to monitor file changes and synchronize them with storage locations. A storage location can be a local directory, a remote server, or a git repository.

To start the daemon, use `watchsync start`, and to stop it, use `watchsync stop`. If you want to restart the daemon to reread configuration changes, use `watchsync reload`.

### Storage Locations
To manage storage locations, use the command `watchsync store`.

You can list storage locations with `watchsync store list`, add a storage location with `watchsync store add NAME TYPE PATH`, and remove one with `watchsync store del NAME`.

Alternatively, you can edit the configuration file `~/.config/watchsync/config.yaml` to add storage locations manually, but note that the daemon will not pick up changes until you restart it after making modifications.

### Files
To manage the files being monitored, use the command `watchsync file`.

You can list files with `watchsync file list`, add a file with `watchsync file add PATH`, and remove a file with `watchsync file del PATH`.

## Development

This project is developed using TDD. Therefore, any changes or improvements to be added must first include a failing unit test, and then the necessary code must be written to make the test pass.

Install the development dependencies:
```bash
poetry install --with dev
poetry run pre-commit install
```

To run unit tests:
```bash
poetry run python3 -m unittest discover -s tests
```

With coverage:
```bash
poetry run coverage run -m unittest discover -s tests
poetry run coverage report
```
Or you can run the command
```bash
poetry run watchsync
```
