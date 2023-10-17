/*
    This is a base spec file that includes methods declarations, definitions
    and functions to be included in other spec. There are no rules in this file.
    For more information, visit: https://www.certora.com/

*/

/*

    Declaration of methods of the Aave token contract (and harness)

*/ 

methods {
    function totalSupply()                         external returns (uint256)   envfree;
    function balanceOf(address)                    external returns (uint256)   envfree;
    function allowance(address,address)            external returns (uint256)   envfree;
    function increaseAllowance(address, uint256) external;
    function decreaseAllowance(address, uint256) external;
    function transfer(address,uint256) external;
    function transferFrom(address,address,uint256) external;
    function permit(address,address,uint256,uint256,uint8,bytes32,bytes32) external;

    function delegate(address delegatee) external;
    function metaDelegate(address,address,uint256,uint8,bytes32,bytes32) external;
    function metaDelegateByType(address,address,uint8,uint256,uint8,bytes32,bytes32) external;
    function getPowerCurrent(address, IGovernancePowerDelegationToken.GovernancePowerType) external returns (uint256) envfree;

    function getBalance(address user) external returns (uint104) envfree;
    function getDelegatedPropositionBalance(address user) external returns (uint72) envfree;
    function getDelegatedVotingBalance(address user) external returns (uint72) envfree;
    function getDelegatingProposition(address user) external returns (bool) envfree;
    function getDelegatingVoting(address user) external returns (bool) envfree;
    function getVotingDelegatee(address user) external returns (address) envfree;
    function getPropositionDelegatee(address user) external returns (address) envfree;
    function getDelegationMode(address user) external returns (AaveTokenV3Harness.DelegationMode) envfree;
}

definition VOTING_POWER() returns IGovernancePowerDelegationToken.GovernancePowerType = IGovernancePowerDelegationToken.GovernancePowerType.VOTING;
definition PROPOSITION_POWER() returns IGovernancePowerDelegationToken.GovernancePowerType = IGovernancePowerDelegationToken.GovernancePowerType.PROPOSITION;
definition DELEGATED_POWER_DIVIDER() returns uint256 = 10^10;

/**

    Definitions of delegation modes

*/
definition NO_DELEGATION() returns AaveTokenV3Harness.DelegationMode = AaveTokenV3Harness.DelegationMode.NO_DELEGATION;
definition VOTING_DELEGATED() returns AaveTokenV3Harness.DelegationMode = AaveTokenV3Harness.DelegationMode.VOTING_DELEGATED;
definition PROPOSITION_DELEGATED() returns AaveTokenV3Harness.DelegationMode = AaveTokenV3Harness.DelegationMode.PROPOSITION_DELEGATED;
definition FULL_POWER_DELEGATED() returns AaveTokenV3Harness.DelegationMode = AaveTokenV3Harness.DelegationMode.FULL_POWER_DELEGATED;
definition DELEGATING_VOTING(AaveTokenV3Harness.DelegationMode mode) returns bool = 
    mode == VOTING_DELEGATED() || mode == FULL_POWER_DELEGATED();
definition DELEGATING_PROPOSITION(AaveTokenV3Harness.DelegationMode mode) returns bool =
    mode == PROPOSITION_DELEGATED() || mode == FULL_POWER_DELEGATED();

definition AAVE_MAX_SUPPLY() returns uint256 = 16000000 * 10^18;
definition SCALED_MAX_SUPPLY() returns mathint = AAVE_MAX_SUPPLY() / DELEGATED_POWER_DIVIDER();


/**

    Functions

*/

function normalize(uint256 amount) returns mathint {
    return amount / DELEGATED_POWER_DIVIDER() * DELEGATED_POWER_DIVIDER();
}

function validDelegationMode(address user) returns bool {
    AaveTokenV3Harness.DelegationMode state = getDelegationMode(user);
    return state == AaveTokenV3Harness.DelegationMode.NO_DELEGATION ||
        state == AaveTokenV3Harness.DelegationMode.VOTING_DELEGATED ||
        state == AaveTokenV3Harness.DelegationMode.PROPOSITION_DELEGATED ||
        state == AaveTokenV3Harness.DelegationMode.FULL_POWER_DELEGATED;
}

function validAmount(uint256 amt) returns bool {
    return amt < AAVE_MAX_SUPPLY();
}
