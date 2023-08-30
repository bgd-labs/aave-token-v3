// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {EthereumScript} from 'aave-helpers/ScriptUtils.sol';
import {UpdateAaveTokenPayload} from '../src/payload/UpdateAaveTokenPayload.sol';

contract DeployUpdateAaveTokenPayload is EthereumScript {
  address public constant AAVE_IMPL = address(1);

  // TODO: this should be get from address-book
  function run() external broadcast {
    new UpdateAaveTokenPayload(AAVE_IMPL);
  }
}
