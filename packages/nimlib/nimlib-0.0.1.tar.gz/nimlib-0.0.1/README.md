# Nimble Libraries

It provides common libraries reusable by miners, validators and network operators.

# Development

### Virtual Env

```bash
# create env & activate
make env
source ./nbenv/bin/activate

# install dependencies
python3 -m pip install -e ./

# clean env
deactivate
make clean
```

### Install

```bash
# pip install option
$ pip3 install nimlib

# test install from python
import nimlib

# cuda dependency for cubit install - python 3.10 example
pip install https://github.com/nimble-technology/cubit/releases/download/v1.1.2/cubit-1.1.2-cp310-cp310-linux_x86_64.whl
```

# Wallet

Each wallet has a coldkey. Each coldkey may contain multiple hotkeys and each hotkey belong to a single coldkey. Coldkeys are for secure fund management like transfer, staking, and fund storage. Hotkeys are for all online operations like signing, mining and validating.


```bash
# wallet creation in python
import nimlib
wallet = nimlib.wallet()
wallet.create_new_coldkey()
wallet.create_new_hotkey()
# Sign data with the keypair.
wallet.coldkey.sign( data )
```

### Release (Core Contributors Only)

Run the following command to create dist folder
```bash
python setup.py sdist
```

Then use the following command to publish to pypi
```bash
twine upload dist/nimlib-{version}.tar.gz
```
