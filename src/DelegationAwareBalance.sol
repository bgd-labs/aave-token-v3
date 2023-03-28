// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

enum DelegationState {
  NO_DELEGATION,
  VOTING_DELEGATED,
  PROPOSITION_DELEGATED,
  FULL_POWER_DELEGATED
}

struct DelegationAwareBalance {
  uint104 balance;
  uint72 delegatedPropositionBalance;
  uint72 delegatedVotingBalance;
  DelegationState delegationState;
}
