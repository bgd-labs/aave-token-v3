/*
    This is a base spec file that includes methods declarations, definitions
    and functions to be included in other spec. There are no rules in this file.
    For more information, visit: https://www.certora.com/

*/

/**

    Declaration of methods of the Aave token contract (and harness)

*/ 

methods {
    totalSupply()                         returns (uint256)   envfree
    balanceOf(address)                    returns (uint256)   envfree
    allowance(address,address)            returns (uint256)   envfree
    increaseAllowance(address, uint256)
    decreaseAllowance(address, uint256)
    transfer(address,uint256)
    transferFrom(address,address,uint256)
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32)

    delegate(address delegatee)
    metaDelegate(address,address,uint256,uint8,bytes32,bytes32)
    metaDelegateByType(address,address,uint8,uint256,uint8,bytes32,bytes32)
    getPowerCurrent(address user, uint8 delegationType) returns (uint256) envfree

    getBalance(address user) returns (uint104) envfree
    getDelegatedPropositionBalance(address user) returns (uint72) envfree
    getDelegatedVotingBalance(address user) returns (uint72) envfree
    getDelegatingProposition(address user) returns (bool) envfree
    getDelegatingVoting(address user) returns (bool) envfree
    getVotingDelegate(address user) returns (address) envfree
    getPropositionDelegate(address user) returns (address) envfree
    getDelegationState(address user) returns (uint8) envfree
}

definition VOTING_POWER() returns uint8 = 0;
definition PROPOSITION_POWER() returns uint8 = 1;
definition DELEGATED_POWER_DIVIDER() returns uint256 = 10^10;

/**

    Definitions of delegation states

*/
definition NO_DELEGATION() returns uint8 = 0;
definition VOTING_DELEGATED() returns uint8 = 1;
definition PROPOSITION_DELEGATED() returns uint8 = 2;
definition FULL_POWER_DELEGATED() returns uint8 = 3;
definition DELEGATING_VOTING(uint8 state) returns bool = 
    state == VOTING_DELEGATED() || state == FULL_POWER_DELEGATED();
definition DELEGATING_PROPOSITION(uint8 state) returns bool =
    state == PROPOSITION_DELEGATED() || state == FULL_POWER_DELEGATED();

definition AAVE_MAX_SUPPLY() returns uint256 = 16000000 * 10^18;
definition SCALED_MAX_SUPPLY() returns uint256 = AAVE_MAX_SUPPLY() / DELEGATED_POWER_DIVIDER();


/**

    Functions

*/

function normalize(uint256 amount) returns uint256 {
    return to_uint256(amount / DELEGATED_POWER_DIVIDER() * DELEGATED_POWER_DIVIDER());
}

function validDelegationState(address user) returns bool {
    return getDelegationState(user) < 4;
}

function validAmount(uint256 amt) returns bool {
    return amt < AAVE_MAX_SUPPLY();
}
