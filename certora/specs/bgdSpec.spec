// using DelegationAwareBalance from "./BaseAaveToken.sol";

// issues:
// for enum, just use 0 (voting) and 1 (proposition) or local definition
// for struct use harness that replaces reads and writes with solidity functions

methods{
    totalSupply() returns (uint256) envfree
    balanceOf(address addr) returns (uint256) envfree
    transfer(address to, uint256 amount) returns (bool)
    transferFrom(address from, address to) returns (bool)

    _votingDelegateeV2(address) returns (address)
    _propositionDelegateeV2(address) returns (address)
    DELEGATED_POWER_DIVIDER() returns (uint256)
    DELEGATE_BY_TYPE_TYPEHASH() returns (bytes32)
    DELEGATE_TYPEHASH() returns (bytes32)
    // _delegationMoveByType(uint104, uint104, address, GovernancePowerType delegationType, function(uint72, uint72) returns (uint72) operation)
    // _delegationMove(address, DelegationAwareBalance userState, uint104, uint104, function(uint72, uint72) returns (uint72) operation)
    _transferWithDelegation(address, address, uint256)
    // _getDelegatedPowerByType(DelegationAwareBalance userState, GovernancePowerType delegationType) returns (uint72)
    // _getDelegateeByType(address, DelegationAwareBalance userState, GovernancePowerType delegationType) returns (address)
    // _updateDelegateeByType(address, GovernancePowerType delegationType, address)
    // _updateDelegationFlagByType(DelegationAwareBalance userState, GovernancePowerType delegationType, bool) returns (DelegationAwareBalance)
    // _delegateByType(address, address, GovernancePowerType delegationType)
    // delegateByType(address, GovernancePowerType delegationType)
    delegate(address delegatee)
    // getDelegateeByType(address delegator, GovernancePowerType delegationType) returns (address)
    // getPowerCurrent(address, GovernancePowerType delegationType) returns (uint256)
    // metaDelegateByType(address, address, GovernancePowerType delegationType, uint256, uint8, bytes32, bytes32)
    metaDelegate(address, address, uint256, uint8, bytes32, bytes32)
    // enum GovernancePowerType {
    //     VOTING,
    //     PROPOSITION
    // }
    getPowerCurrent(address user, uint8 delegationType) returns (uint256) envfree

    getBalance(address user) returns (uint104) envfree
    getDelegatedPropositionBalance(address user) returns (uint72) envfree
    getDelegatedVotingBalance(address user) returns (uint72) envfree
    getDelegatingProposition(address user) returns (bool) envfree
    getDelegatingVoting(address user) returns (bool) envfree
}

definition VOTING_POWER() returns uint8 = 0;
definition PROPOSITION_POWER() returns uint8 = 1;

// for test - it shouldnt pass
// invariant ZeroAddressNoDelegation()
//     getPowerCurrent(0, 0) == 0 && getPowerCurrent(0, 1) == 0

// The total power (of one type) of all users in the system is less or equal than 
// the sum of balances of all AAVE holders (totalSupply of AAVE token)

// accumulator for a  sum of proposition voting power
ghost mathint sumDelegatedProposition {
    init_state axiom forall uint256 t. sumDelegatedProposition == 0;
}

ghost mathint sumBalances {
    init_state axiom forall uint256 t. sumBalances == 0;
}

/*
  update proposition balance on each store
 */
hook Sstore _balances[KEY address user].delegatedPropositionBalance uint72 balance
    (uint72 old_balance) STORAGE {
        sumDelegatedProposition = sumDelegatedProposition + to_mathint(balance) - to_mathint(old_balance);
    }

// try to rewrite using power.spec in aave-tokenv2 customer code
hook Sstore _balances[KEY address user].balance uint104 balance
    (uint104 old_balance) STORAGE {
        sumBalances = sumBalances + to_mathint(balance) - to_mathint(old_balance);
    }

invariant sumDelegatedPropositionCorrectness() sumDelegatedProposition <= totalSupply() { 
  // fails
  preserved transfer(address to, uint256 amount) with (env e)
         {
            require(balanceOf(e.msg.sender) + balanceOf(to)) < totalSupply();
         }
   preserved transferFrom(address from, address to, uint256 amount) with (env e)
        {
        require(balanceOf(from) + balanceOf(to)) < totalSupply();
        }
}

rule totalSupplyCorrectness(method f) {
    env e;
    calldataarg args;

    require sumBalances == to_mathint(totalSupply());
    f(e, args);
    assert sumBalances == to_mathint(totalSupply());
}

// doesn't work cause we can start with a state in which an address can have delegated balance field 
// larger than total supply.
// rule sumDelegatedPropositionCorrect(method f) {
//     env e;
//     calldataarg args;

//     uint256 supplyBefore = totalSupply();
//     require sumDelegatedProposition <= supplyBefore;
//     f(e, args);
//     uint256 supplyAfter = totalSupply();
//     assert sumDelegatedProposition <= supplyAfter;
// }


rule transferUnitTest() {
    env e;
    address to;
    uint256 amount;
    require(to != e.msg.sender);

    uint256 powerToBefore = getPowerCurrent(to, VOTING_POWER());
    uint256 powerSenderBefore = getPowerCurrent(e.msg.sender, VOTING_POWER());
    transfer(e, to, amount);
    uint256 powerToAfter = getPowerCurrent(to, VOTING_POWER());

    assert powerToAfter == powerToBefore + powerSenderBefore;
}