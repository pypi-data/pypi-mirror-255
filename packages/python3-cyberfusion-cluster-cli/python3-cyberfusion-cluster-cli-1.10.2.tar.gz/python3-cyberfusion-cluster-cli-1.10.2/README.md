# python3-cyberfusion-cluster-cli

CLI for Cyberfusion Cluster API.

# Install

## Recommended

    curl https://cli-downloads.cyberfusion.io/install.sh | bash

## PyPI (expert only)

Run one of the following commands to install the package from PyPI.

Python version 3.9 or higher is required.

    # Default

    pip3 install python3-cyberfusion-cluster-cli

    # Alternative: with Borg support
    #
    # This installs dependencies needed to manage Borg, which do not work on all
    # operating systems.

    pip3 install python3-cyberfusion-cluster-cli[borg]


# Configure

When running the CLI for the first time, run the following command:

    clusterctl setup

You are then prompted for API credentials.

A config file is created in `~/.config/cyberfusion/cyberfusion.cfg`.

# Usage

The CLI provides commands for all relevant API endpoints.

Run the following command for help:

    clusterctl -h

# Tests

No tests are present.
