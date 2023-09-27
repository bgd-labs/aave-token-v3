# $AAVE token v3

<p align="center">
<img src="./aave-token-v3.png" width="300">
</p>

<br>

Next iteration of the AAVE token, optimized for its usage as voting asset on Aave Governance v3.

More detailed description and specification [HERE](./properties.md)

<br>

## Setup

This repository requires having Foundry installed in the running machine. Instructions on how to do it [HERE](https://github.com/foundry-rs/foundry#installation).

After having installed Foundry:
1. Add a `.env` file with properly configured `ETH_RPC_URL` and `FORK_BLOCK`, following the example on `.env.example` 
2. `make test` to run the simulation tests.

<br>

## Security

- Internal testing and review by the BGD Labs team, but in terms of logic and upgradeability considerations.
    - [Test suite](./src/test/).
    - [Storage layout diffs](./diffs/)
- Security review and properties checking (formal verification) by [Certora](https://www.certora.com/), service provider of the Aave DAO.
    - [Properties](./certora/README.md)
    - [Reports](./certora/reports/Formal_Verification_Report_AAVE_Token_V3.pdf)

<br>

## Copyright

Copyright © 2023, Aave DAO, represented by its governance smart contracts.

Created by [BGD Labs](https://bgdlabs.com/).

[MIT license](./LICENSE)