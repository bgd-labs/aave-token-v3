// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import 'forge-std/Test.sol';
import {AaveTokenV3} from '../../AaveTokenV3.sol';
import {IAaveTokenV3} from '../../interfaces/IAaveTokenV3.sol';
import {IBaseAdminUpgradeabilityProxy} from './IBaseAdminUpgradeabilityProxy.sol';

abstract contract AaveUtils is Test {
  address[] public AAVE_HOLDERS;
  IAaveTokenV3 public constant AAVE_TOKEN =
    IAaveTokenV3(0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9);

  address public constant AAVE_V2_IMPLEMENTATION = 0xC13eac3B4F9EED480045113B7af00F7B5655Ece8;

  address public constant AAVE_TOKEN_PROXY_ADMIN = 0x61910EcD7e8e942136CE7Fe7943f956cea1CC2f7;
  address public AAVE_IMPLEMENTATION_V3;

  struct Permit {
    address owner;
    address spender;
    uint256 value;
    uint256 nonce;
    uint256 deadline;
  }

  struct DelegateByType {
    address delegator;
    address delegatee;
    IAaveTokenV3.GovernancePowerType delegationType;
    uint256 nonce;
    uint256 deadline;
  }

  struct Delegate {
    address delegator;
    address delegatee;
    uint256 nonce;
    uint256 deadline;
  }

  constructor() {
    AAVE_IMPLEMENTATION_V3 = address(new AaveTokenV3());
    AAVE_HOLDERS = new address[](10);
    AAVE_HOLDERS = [
      0x4da27a545c0c5B758a6BA100e3a049001de870f5,
      0xFFC97d72E13E01096502Cb8Eb52dEe56f74DAD7B,
      0x25F2226B597E8F9514B3F68F00f494cF4f286491,
      0xC697051d1C6296C24aE3bceF39acA743861D9A81,
      0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8,
      0x317625234562B1526Ea2FaC4030Ea499C5291de4,
      0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503,
      0xF977814e90dA44bFA03b6295A0616a897441aceC,
      0x26a78D5b6d7a7acEEDD1e6eE3229b372A624d8b7,
      0x28C6c06298d514Db089934071355E5743bf21d60
    ];
  }

  function updateAaveImplementation(address newImplementation) public {
    vm.prank(AAVE_TOKEN_PROXY_ADMIN);
    IBaseAdminUpgradeabilityProxy(address(AAVE_TOKEN)).upgradeTo(newImplementation);
  }

  function revertAaveImplementationUpdate() public {
    updateAaveImplementation(AAVE_V2_IMPLEMENTATION);
  }

  // computes the hash of the fully encoded EIP-712 message for the domain, which can be used to recover the signer
  function getPermitTypedDataHash(
    Permit memory _permit,
    bytes32 domainSeparator
  ) public view returns (bytes32) {
    return
      keccak256(
        abi.encodePacked(
          '\x19\x01',
          domainSeparator,
          keccak256(
            abi.encode(
              AAVE_TOKEN.PERMIT_TYPEHASH(),
              _permit.owner,
              _permit.spender,
              _permit.value,
              _permit.nonce,
              _permit.deadline
            )
          )
        )
      );
  }

  // computes the hash of the fully encoded EIP-712 message for the domain, which can be used to recover the signer
  function getMetaDelegateByTypedDataHash(
    DelegateByType memory _delegateByType,
    bytes32 domainSeparator
  ) public view returns (bytes32) {
    return
      keccak256(
        abi.encodePacked(
          '\x19\x01',
          domainSeparator,
          keccak256(
            abi.encode(
              AAVE_TOKEN.DELEGATE_BY_TYPE_TYPEHASH(),
              _delegateByType.delegator,
              _delegateByType.delegatee,
              _delegateByType.delegationType,
              _delegateByType.nonce,
              _delegateByType.deadline
            )
          )
        )
      );
  }

  // computes the hash of the fully encoded EIP-712 message for the domain, which can be used to recover the signer
  function getMetaDelegateDataHash(
    Delegate memory _delegate,
    bytes32 domainSeparator
  ) public view returns (bytes32) {
    return
      keccak256(
        abi.encodePacked(
          '\x19\x01',
          domainSeparator,
          keccak256(
            abi.encode(
              AAVE_TOKEN.DELEGATE_TYPEHASH(),
              _delegate.delegator,
              _delegate.delegatee,
              _delegate.nonce,
              _delegate.deadline
            )
          )
        )
      );
  }
}
