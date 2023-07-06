// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {AaveTokenV3} from '../src/AaveTokenV3.sol';

abstract contract AaveTokenScript {
  function _deploy() internal returns (address) {
    AaveTokenV3 aaveToken = new AaveTokenV3();
    aaveToken.initialize();

    return address(aaveToken);
  }
}
