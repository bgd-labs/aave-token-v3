// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {AaveTokenV3} from "./storage_harness/AaveTokenV3.sol";

contract AaveTokenV3Harness is AaveTokenV3 {
    function getBalance(address user) view public returns (uint104) {
    return _balances[user].balance;
   }

   function getDelegatedPropositionBalance(address user) view public returns (uint72) {
    return _balances[user].delegatedPropositionBalance;
   }


   function getDelegatedVotingBalance(address user) view public returns (uint72) {
    return _balances[user].delegatedVotingBalance;
   }


   function getDelegatingProposition(address user) view public returns (bool) {
    uint8 state = _balances[user].delegationState;
    return state == uint8(DelegationState.PROPOSITION_DELEGATED) ||
        state == uint8(DelegationState.FULL_POWER_DELEGATED);
   }


   function getDelegatingVoting(address user) view public returns (bool) {
    uint8 state = _balances[user].delegationState;
    return state == uint8(DelegationState.VOTING_DELEGATED) ||
        state == uint8(DelegationState.FULL_POWER_DELEGATED);
   }

   function getVotingDelegate(address user) view public returns (address) {
    return _votingDelegateeV2[user];
   }

   function getPropositionDelegate(address user) view public returns (address) {
    return _propositionDelegateeV2[user];
   }

   function getDelegationState(address user) view public returns (uint8) {
    return _balances[user].delegationState;
   }
}