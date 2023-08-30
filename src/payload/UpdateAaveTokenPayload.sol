// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {TransparentUpgradeableProxy} from 'solidity-utils/contracts/transparent-proxy/TransparentUpgradeableProxy.sol';
import {AaveMisc} from 'aave-address-book/AaveMisc.sol';
import {AaveV3Ethereum, AaveV3EthereumAssets} from 'aave-address-book/AaveV3Ethereum.sol';
import {AaveTokenV3} from '../AaveTokenV3.sol';

contract UpdateAaveTokenPayload {
  address public immutable AAVE_IMPL;

  constructor(address aaveImpl) {
    AAVE_IMPL = aaveImpl;
  }

  function execute() external {
    // update Aave token impl
    TransparentUpgradeableProxy(payable(AaveV3EthereumAssets.AAVE_UNDERLYING)).upgradeToAndCall(
      AAVE_IMPL,
      abi.encodeWithSelector(AaveTokenV3.initialize.selector)
    );

    // move aave token proxy admin owner from Long Executor to ProxyAdminLong
    TransparentUpgradeableProxy(payable(AaveV3EthereumAssets.AAVE_UNDERLYING)).changeAdmin(
      AaveMisc.PROXY_ADMIN_ETHEREUM_LONG
    );
  }
}
