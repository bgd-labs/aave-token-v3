// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Test} from 'forge-std/Test.sol';
import {GovHelpers} from 'aave-helpers/GovHelpers.sol';
import {ProxyHelpers} from 'aave-helpers/ProxyHelpers.sol';
import {AaveGovernanceV2} from 'aave-address-book/AaveGovernanceV2.sol';
import {AaveV3Ethereum, AaveV3EthereumAssets} from 'aave-address-book/AaveV3Ethereum.sol';
import {ProtocolV3TestBase, ReserveConfig} from 'aave-helpers/ProtocolV3TestBase.sol';

import {AaveTokenV3} from '../../AaveTokenV3.sol';
import {UpdateAaveTokenPayload} from '../../payload/UpdateAaveTokenPayload.sol';

contract UpdateAaveTokenPayloadTest is ProtocolV3TestBase {
  function setUp() public {
    vm.createSelectFork(vm.rpcUrl('mainnet'), 17635720);
  }

  function testExecute() public {
    AaveTokenV3 aaveToken = new AaveTokenV3();

    UpdateAaveTokenPayload payload = new UpdateAaveTokenPayload(address(aaveToken));

    GovHelpers.executePayload(vm, address(payload), AaveGovernanceV2.LONG_EXECUTOR);

    address newImpl = ProxyHelpers.getInitializableAdminUpgradeabilityProxyImplementation(
      vm,
      AaveV3EthereumAssets.AAVE_UNDERLYING
    );

    assertEq(newImpl, address(aaveToken));

    ReserveConfig[] memory allConfigs = _getReservesConfigs(AaveV3Ethereum.POOL);

    e2eTestAsset(
      AaveV3Ethereum.POOL,
      _findReserveConfig(allConfigs, AaveV3EthereumAssets.USDC_UNDERLYING),
      _findReserveConfig(allConfigs, AaveV3EthereumAssets.AAVE_UNDERLYING)
    );
  }
}
