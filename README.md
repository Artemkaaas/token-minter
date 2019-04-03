# Token minter

This is the simple GUI utility for minting tokens based on [Indy-Sdk](https://github.com/hyperledger/indy-sdk) and [Libsovtoken](https://github.com/sovrin-foundation/libsovtoken) libraries.

## Prerequisites
### System Dependencies
* Python3
* Indy-SDK - https://github.com/hyperledger/indy-sdk#installing-the-sdk
* Libsovtoken - do the same steps as for Libindy but use at the end `sudo apt-get install -y libsovtoken`.
* python3-tk - `sudo apt-get install -y python3-tk`
### Data
* Wallet with a DID on that ledger. This can be done using the [Indy-CLI](https://github.com/hyperledger/indy-sdk).

### Run
    `python3 src/main.py`