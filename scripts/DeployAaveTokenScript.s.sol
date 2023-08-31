// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {AaveTokenV3} from '../src/AaveTokenV3.sol';
import {EthereumScript} from 'aave-helpers/ScriptUtils.sol';

contract DeployAaveToken is EthereumScript {
  function run() external broadcast {
    AaveTokenV3 aaveToken = new AaveTokenV3();
    aaveToken.initialize();
  }
}
