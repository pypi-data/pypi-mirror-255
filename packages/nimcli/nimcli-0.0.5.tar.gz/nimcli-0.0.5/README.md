# Nimble Command Line (CLI) Tooling

It provides cli tools for miners, validators and network operators.

# Development

### Virtual Env

```bash
# create env and activate
make env
source ./nbenv/bin/activate

# install dependencies
brew install python@3.11
brew link python@3.11
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install -e ./

# format
black *py
black commands/*py

# clean after code dev
deactivate
make clean
```
### Install

```bash
# installer option
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/nimble-technology/nimble-cli/main/scripts/install.sh)"

# pip install option
$ pip3 install nimcli

# test install from command line
# usage: nimcli <command> <command args>
# commands:
#   subnets (s, subnet) - Commands for managing and viewing subnetworks.
#   root (r, roots) - Commands for managing and viewing the root network.
#   wallet (w, wallets) - Commands for managing and viewing wallets.
#   stake (st, stakes) - Commands for staking and removing stake from hotkey accounts.
#   sudo (su, sudos) - Commands for subnet management.
#   legacy (l) - Miscellaneous commands.

# test install
$ nimcli --help
```

### Wallet CLI as an Example

Each wallet has a coldkey. Each coldkey may contain multiple hotkeys and each hotkey belong to a single coldkey. Coldkeys are for secure fund management like transfer, staking, and fund storage. Hotkeys are for all online operations like signing, mining and validating.

```bash
# use nimcli with wallet subcommand or alias w.
$ nimcli wallet new_coldkey
$ nimcli wallet new_hotkey

$ nimcli wallet regen_coldkey --mnemonic **** *** **** **** ***** **** *** **** **** **** ***** *****

# keys are available here: ~/.nimble/wallets
$ nimcli wallet list

# more commands
$ nimcli wallet list
$ nimcli wallet transfer
```

### Release (Core Contributors Only)

Run the following command to create dist folder
```bash
python setup.py sdist
```

Then use the following command to publish to pypi
```bash
twine upload dist/nim-cli-{version}.tar.gz
```
