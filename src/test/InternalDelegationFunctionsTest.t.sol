// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IERC20Metadata} from '../../lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol';
import {AaveTokenV3} from '../AaveTokenV3.sol';

import {AaveUtils, console} from './AaveUtils.sol';

contract StorageTest is AaveTokenV3, AaveUtils {
  function setUp() public {}

  function testFor_getDelegatedPowerByType() public {
    DelegationAwareBalance memory userState;
    userState.delegatedPropositionBalance = 100;
    userState.delegatedVotingBalance = 200;
    assertEq(
      _getDelegatedPowerByType(userState, GovernancePowerType.VOTING),
      userState.delegatedVotingBalance
    );
    assertEq(
      _getDelegatedPowerByType(userState, GovernancePowerType.PROPOSITION),
      userState.delegatedPropositionBalance
    );
  }

  function testFor_getDelegateeByType() public {
    address user = address(0x1);
    address user2 = address(0x2);
    address user3 = address(0x3);
    DelegationAwareBalance memory userState;

    _votingDelegateeV2[user] = address(user2);
    _propositionDelegateeV2[user] = address(user3);

    userState.delegatingVoting = true;
    userState.delegatingProposition = false;
    assertEq(_getDelegateeByType(user, userState, GovernancePowerType.VOTING), user2);
    assertEq(_getDelegateeByType(user, userState, GovernancePowerType.PROPOSITION), address(0));

    userState.delegatingVoting = false;
    userState.delegatingProposition = true;
    assertEq(_getDelegateeByType(user, userState, GovernancePowerType.VOTING), address(0));

    assertEq(_getDelegateeByType(user, userState, GovernancePowerType.PROPOSITION), user3);
  }
}
