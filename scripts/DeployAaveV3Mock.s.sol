// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

//import 'forge-std/console.sol';
import 'forge-std/Script.sol';
import {TransparentUpgradeableProxy} from 'solidity-utils/contracts/transparent-proxy/TransparentUpgradeableProxy.sol';
import {AaveMisc} from 'aave-address-book/AaveMisc.sol';
import {AaveV3Ethereum, AaveV3EthereumAssets} from 'aave-address-book/AaveV3Ethereum.sol';
import {AaveTokenV3} from '../src/AaveTokenV3.sol';
import {ITransparentProxyFactory} from "solidity-utils/contracts/transparent-proxy/TransparentProxyFactory.sol";

contract AaveTokenV3Mock is AaveTokenV3 {
  function name() public view virtual override returns (string memory) {
    return 'AAVE Token';
  }

  function symbol() public view virtual override returns (string memory) {
    return 'AAVE';
  }
  function mintToken() external {
    address to = msg.sender;
    uint104 toBalanceBefore = _balances[to].balance;

    _balances[to].balance = toBalanceBefore + uint104(1000 ether);

    _afterTokenTransfer(address(0), to, 0, toBalanceBefore, 1000 ether);

  }
}


contract DeployAaveV3Mock is Script {
  function run() public {
    vm.startBroadcast();
    AaveTokenV3 aaveTokenImpl = new AaveTokenV3Mock();
    aaveTokenImpl.initialize();

    ITransparentProxyFactory proxyFactory = ITransparentProxyFactory(0x98C977c66266366dbEc8E4Ca049A0e1Db7D26428);//new TransparentProxyFactory();
    address proxyAdmin = 0x48a93f60B3F3f741d864Fdaf6E85A5634e71d1D8;//proxyFactory.createProxyAdmin(msg.sender);

    address aaveToken = proxyFactory
      .createDeterministic(
      address(aaveTokenImpl),
      proxyAdmin,
      abi.encodeWithSelector(
        AaveTokenV3.initialize.selector
      ),
      keccak256('Aave token salt')
    );

    vm.stopBroadcast();
//    console.log('aave token', aaveToken);
//    console.log('proxyAdmin', proxyAdmin);
//    console.log('proxyFactory', address(proxyFactory));
  }
}
