// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IGovernancePowerDelegationToken} from '../interfaces/IGovernancePowerDelegationToken.sol';
import {AaveUtils} from './utils/AaveUtils.sol';

contract AaveTokenV3Test is AaveUtils {
  function setUp() public {
    updateAaveImplementation(AAVE_IMPLEMENTATION_V3);
  }

  function testPermit() public {
    uint256 privateKey = 0xB26ECB;
    address owner = vm.addr(privateKey);
    address spender = address(5);
    uint256 amountToPermit = 1000 ether;

    Permit memory permitParams = Permit({
      owner: owner,
      spender: spender,
      value: amountToPermit,
      nonce: AAVE_TOKEN._nonces(owner),
      deadline: type(uint256).max
    });

    bytes32 digest = getPermitTypedDataHash(permitParams, AAVE_TOKEN.DOMAIN_SEPARATOR());
    (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, digest);

    AAVE_TOKEN.permit(
      permitParams.owner,
      permitParams.spender,
      permitParams.value,
      permitParams.deadline,
      v,
      r,
      s
    );

    uint256 allowance = AAVE_TOKEN.allowance(owner, spender);
    assertTrue(allowance == amountToPermit);
  }

  // FORK BLOCK: 15319194
  function testDelegateByType() public {
    address delegator = 0xA7499Aa6464c078EeB940da2fc95C6aCd010c3Cc;
    address delegatee = address(5);

    uint256 delegateePropositionPowerBefore = AAVE_TOKEN.getPowerCurrent(
      delegatee,
      IGovernancePowerDelegationToken.GovernancePowerType.PROPOSITION
    );

    vm.startPrank(delegator);
    AAVE_TOKEN.delegateByType(
      delegatee,
      IGovernancePowerDelegationToken.GovernancePowerType.PROPOSITION
    );
    vm.stopPrank();

    uint256 delegateePropositionPowerAfter = AAVE_TOKEN.getPowerCurrent(
      delegatee,
      IGovernancePowerDelegationToken.GovernancePowerType.PROPOSITION
    );

    assertTrue(
      delegateePropositionPowerAfter != 0 &&
      delegateePropositionPowerAfter != delegateePropositionPowerBefore
    );
  }

  // FORK BLOCK: 15319194
  function testMetaDelegateByType() public {
    uint256 privateKey = 0xB26ECB;
    address delegator = vm.addr(privateKey);
    address delegatee = address(5);

    // Transfer AAVE to delegator to get non-zero governance powers on delegator
    vm.startPrank(AAVE_HOLDERS[0]);
    AAVE_TOKEN.transfer(
      delegator,
      1 ether
    );
    vm.stopPrank();

    uint256 delegateePropositionPowerBefore = AAVE_TOKEN.getPowerCurrent(
      delegatee,
      IGovernancePowerDelegationToken.GovernancePowerType.PROPOSITION
    );

    DelegateByType memory delegateByTypeParams = DelegateByType({
      delegator: delegator,
      delegatee: delegatee,
      delegationType: IGovernancePowerDelegationToken.GovernancePowerType.PROPOSITION,
      nonce: AAVE_TOKEN._nonces(delegator),
      deadline: type(uint256).max
    });

    bytes32 digest = getMetaDelegateByTypedDataHash(delegateByTypeParams, AAVE_TOKEN.DOMAIN_SEPARATOR());
    (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, digest);

    AAVE_TOKEN.metaDelegateByType(
      delegateByTypeParams.delegator,
      delegateByTypeParams.delegatee,
      delegateByTypeParams.delegationType,
      delegateByTypeParams.deadline,
      v,
      r,
      s
    );

    uint256 delegateePropositionPowerAfter = AAVE_TOKEN.getPowerCurrent(
      delegatee,
      IGovernancePowerDelegationToken.GovernancePowerType.PROPOSITION
    );

    assertTrue(
      delegateePropositionPowerAfter != 0 &&
      delegateePropositionPowerAfter != delegateePropositionPowerBefore
    );
  }

  // FORK BLOCK: 15319194
  function testDelegate() public {
    address delegator = 0xA7499Aa6464c078EeB940da2fc95C6aCd010c3Cc;
    address delegatee = address(5);

    (uint256 delegateeVotingPowerBefore, uint256 delegateePropositionPowerBefore) = AAVE_TOKEN.getPowersCurrent(delegatee);

    vm.startPrank(delegator);
    AAVE_TOKEN.delegate(delegatee);
    vm.stopPrank();

    (uint256 delegateeVotingPowerAfter, uint256 delegateePropositionPowerAfter) = AAVE_TOKEN.getPowersCurrent(delegatee);

    assertTrue(
      delegateePropositionPowerAfter != 0 &&
      delegateePropositionPowerAfter != delegateePropositionPowerBefore
    );
    assertTrue(
      delegateeVotingPowerAfter != 0 &&
      delegateeVotingPowerAfter != delegateeVotingPowerBefore
    );
  }

  // FORK BLOCK: 15319194
  function testMetaDelegate() public {
    uint256 privateKey = 0xB26ECB;
    address delegator = vm.addr(privateKey);
    address delegatee = address(5);

    // Transfer AAVE to delegator to get non-zero governance powers on delegator
    vm.startPrank(AAVE_HOLDERS[0]);
    AAVE_TOKEN.transfer(
      delegator,
      1 ether
    );
    vm.stopPrank();

    (uint256 delegateeVotingPowerBefore, uint256 delegateePropositionPowerBefore) = AAVE_TOKEN.getPowersCurrent(delegatee);

    Delegate memory delegateByTypeParams = Delegate({
      delegator: delegator,
      delegatee: delegatee,
      nonce: AAVE_TOKEN._nonces(delegator),
      deadline: type(uint256).max
    });

    bytes32 digest = getMetaDelegateDataHash(delegateByTypeParams, AAVE_TOKEN.DOMAIN_SEPARATOR());
    (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, digest);

    AAVE_TOKEN.metaDelegate(
      delegateByTypeParams.delegator,
      delegateByTypeParams.delegatee,
      delegateByTypeParams.deadline,
      v,
      r,
      s
    );

    (uint256 delegateeVotingPowerAfter, uint256 delegateePropositionPowerAfter) = AAVE_TOKEN.getPowersCurrent(delegatee);

    assertTrue(
      delegateePropositionPowerAfter != 0 &&
      delegateePropositionPowerAfter != delegateePropositionPowerBefore
    );
    assertTrue(
      delegateeVotingPowerAfter != 0 &&
      delegateeVotingPowerAfter != delegateeVotingPowerBefore
    );
  }
}
