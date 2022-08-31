// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IERC20Metadata} from '../../lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol';
import {AaveTokenV3} from '../AaveTokenV3.sol';

import {AaveUtils, console} from './utils/AaveUtils.sol';

contract StorageTest is AaveTokenV3, AaveUtils {
  address constant ECOSYSTEM_RESERVE = 0x25F2226B597E8F9514B3F68F00f494cF4f286491;
  address constant EOA = 0x687871030477bf974725232F764aa04318A8b9c8;
  AaveTokenV3 constant AAVE_V3_TOKEN = AaveTokenV3(address(AAVE_TOKEN));

  function setUp() public {
    updateAaveImplementation(AAVE_IMPLEMENTATION_V3);
  }

  function _removePrecision(uint256 number) internal pure returns (uint256) {
    return (number / POWER_SCALE_FACTOR) * POWER_SCALE_FACTOR;
  }

  function testDelegation() public {
    uint256 currentVotingPower = AAVE_V3_TOKEN.getPowerCurrent(
      ECOSYSTEM_RESERVE,
      GovernancePowerType.VOTING
    );
    uint256 currentPropositionPower = AAVE_V3_TOKEN.getPowerCurrent(
      ECOSYSTEM_RESERVE,
      GovernancePowerType.PROPOSITION
    );

    vm.startPrank(ECOSYSTEM_RESERVE);

    AAVE_V3_TOKEN.delegateByType(EOA, GovernancePowerType.VOTING);

    assertEq(AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.VOTING), 0);
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.VOTING),
      _removePrecision(currentVotingPower)
    );
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.PROPOSITION),
      currentPropositionPower
    );
    assertEq(AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.PROPOSITION), 0);

    AAVE_V3_TOKEN.delegateByType(EOA, GovernancePowerType.PROPOSITION);

    assertEq(AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.VOTING), 0);
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.VOTING),
      _removePrecision(currentVotingPower)
    );
    assertEq(AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.PROPOSITION), 0);
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.PROPOSITION),
      _removePrecision(currentPropositionPower)
    );
  }

  function testRenounceDelegationType() public {
    uint256 currentVotingPower = AAVE_V3_TOKEN.getPowerCurrent(
      ECOSYSTEM_RESERVE,
      GovernancePowerType.VOTING
    );
    uint256 currentPropositionPower = AAVE_V3_TOKEN.getPowerCurrent(
      ECOSYSTEM_RESERVE,
      GovernancePowerType.PROPOSITION
    );

    vm.startPrank(ECOSYSTEM_RESERVE);
    AAVE_V3_TOKEN.delegateByType(EOA, GovernancePowerType.VOTING);
    AAVE_V3_TOKEN.delegateByType(EOA, GovernancePowerType.PROPOSITION);
    vm.stopPrank();

    vm.startPrank(EOA);
    AAVE_V3_TOKEN.renounceDelegatorByType(ECOSYSTEM_RESERVE, GovernancePowerType.VOTING);
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.VOTING),
      currentVotingPower
    );
    assertEq(AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.VOTING), 0);

    AAVE_V3_TOKEN.renounceDelegatorByType(ECOSYSTEM_RESERVE, GovernancePowerType.PROPOSITION);
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.PROPOSITION),
      currentPropositionPower
    );
    assertEq(AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.PROPOSITION), 0);
  }

  function testFailRenounceDelegationTypeNone() public {
    vm.startPrank(EOA);
    AAVE_V3_TOKEN.renounceDelegatorByType(ECOSYSTEM_RESERVE, GovernancePowerType.PROPOSITION);
  }

  function testRenounceDelegationAll() public {
    uint256 currentVotingPower = AAVE_V3_TOKEN.getPowerCurrent(
      ECOSYSTEM_RESERVE,
      GovernancePowerType.VOTING
    );
    uint256 currentPropositionPower = AAVE_V3_TOKEN.getPowerCurrent(
      ECOSYSTEM_RESERVE,
      GovernancePowerType.PROPOSITION
    );

    vm.startPrank(ECOSYSTEM_RESERVE);
    AAVE_V3_TOKEN.delegateByType(EOA, GovernancePowerType.VOTING);
    AAVE_V3_TOKEN.delegateByType(EOA, GovernancePowerType.PROPOSITION);
    vm.stopPrank();

    vm.startPrank(EOA);
    AAVE_V3_TOKEN.renounceDelegator(ECOSYSTEM_RESERVE);
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.VOTING),
      currentVotingPower
    );
    assertEq(AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.VOTING), 0);
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.PROPOSITION),
      currentPropositionPower
    );
    assertEq(AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.PROPOSITION), 0);
  }

  function testRenounceDelegationOne() public {
    uint256 currentVotingPower = AAVE_V3_TOKEN.getPowerCurrent(
      ECOSYSTEM_RESERVE,
      GovernancePowerType.VOTING
    );
    uint256 currentPropositionPower = AAVE_V3_TOKEN.getPowerCurrent(
      ECOSYSTEM_RESERVE,
      GovernancePowerType.PROPOSITION
    );

    vm.startPrank(ECOSYSTEM_RESERVE);
    AAVE_V3_TOKEN.delegateByType(EOA, GovernancePowerType.VOTING);
    vm.stopPrank();

    vm.startPrank(EOA);
    AAVE_V3_TOKEN.renounceDelegator(ECOSYSTEM_RESERVE);
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.VOTING),
      currentVotingPower
    );
    assertEq(AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.VOTING), 0);
    assertEq(
      AAVE_V3_TOKEN.getPowerCurrent(ECOSYSTEM_RESERVE, GovernancePowerType.PROPOSITION),
      currentPropositionPower
    );
    assertEq(AAVE_V3_TOKEN.getPowerCurrent(EOA, GovernancePowerType.PROPOSITION), 0);
  }

  function testFailRenounceDelegationNone() public {
    vm.startPrank(EOA);
    AAVE_V3_TOKEN.renounceDelegator(ECOSYSTEM_RESERVE);
  }
}
