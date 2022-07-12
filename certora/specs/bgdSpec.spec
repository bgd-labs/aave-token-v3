// using DelegationAwareBalance from "./BaseAaveToken.sol";

// issues:
// for enum, just use 0 (voting) and 1 (proposition) or local definition
// for struct use harness that replaces reads and writes with solidity functions

methods{
    totalSupply() returns (uint256) envfree
    balanceOf(address addr) returns (uint256) envfree
    transfer(address to, uint256 amount) returns (bool)
    transferFrom(address from, address to, uint256 amount) returns (bool)

    DELEGATED_POWER_DIVIDER() returns (uint256)
    DELEGATE_BY_TYPE_TYPEHASH() returns (bytes32)
    DELEGATE_TYPEHASH() returns (bytes32)
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
    getVotingDelegate(address user) returns (address) envfree
    getPropositionDelegate(address user) returns (address) envfree
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
    init_state axiom sumDelegatedProposition == 0;
}

ghost mathint sumBalances {
    init_state axiom sumBalances == 0;
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

invariant sumDelegatedPropositionCorrectness() sumDelegatedProposition <= sumBalances { 
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

invariant nonDelegatingBalance(address user)
    !getDelegatingProposition(user) => balanceOf(user) == getDelegatedPropositionBalance(user) {
        preserved transfer(address to, uint256 amount) with (env e)
            {
                require(getVotingDelegate(to) != user);
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

// for non delegating address
rule votingPowerEqualsBalance(address user) {
    uint256 userBalance = balanceOf(user);
    require(!getDelegatingProposition(user));
    require(!getDelegatingVoting(user));
    assert userBalance == getDelegatedPropositionBalance(user) && userBalance == getDelegatedVotingBalance(user);
}

// Verify that the voting delegation balances update correctly
// probably a scaling issue
rule tokenTransferCorrectnessVoting(address from, address to, uint256 amount) {
    env e;

    require(from != 0 && to != 0);

    uint256 balanceFromBefore = balanceOf(from);
    uint256 balanceToBefore = balanceOf(to);

    address fromDelegate = getVotingDelegate(from);
    address toDelegate = getVotingDelegate(to);

    uint256 powerFromDelegateBefore = getPowerCurrent(fromDelegate, VOTING_POWER());
    uint256 powerToDelegateBefore = getPowerCurrent(toDelegate, VOTING_POWER());

    bool isDelegatingVotingFromBefore = getDelegatingVoting(from);
    bool isDelegatingVotingToBefore = getDelegatingVoting(to);

    // non reverting path
    transferFrom(e, from, to, amount);

    uint256 balanceFromAfter = balanceOf(from);
    uint256 balanceToAfter = balanceOf(to);

    address fromDelegateAfter = getVotingDelegate(from);
    address toDelegateAfter = getVotingDelegate(to);

    uint256 powerFromDelegateAfter = getPowerCurrent(fromDelegateAfter, VOTING_POWER());
    uint256 powerToDelegateAfter = getPowerCurrent(toDelegateAfter, VOTING_POWER());

    bool isDelegatingVotingFromAfter = getDelegatingVoting(from);
    bool isDelegatingVotingToAfter = getDelegatingVoting(to);

    assert fromDelegateAfter == toDelegateAfter => powerFromDelegateBefore == powerFromDelegateAfter;

    assert isDelegatingVotingFromBefore => 
        powerFromDelegateAfter - powerFromDelegateBefore == amount ||
        (fromDelegateAfter == toDelegateAfter && powerFromDelegateBefore == powerFromDelegateAfter);
    assert isDelegatingVotingToBefore => 
        powerToDelegateAfter - powerToDelegateBefore == amount  ||
        (fromDelegateAfter == toDelegateAfter && powerToDelegateBefore == powerToDelegateAfter);

}

// If an account is not receiving delegation of power (one type) from anybody, 
// and that account is not delegating that power to anybody, the power of that account
// must be equal to its AAVE balance.

rule powerWhenNotDelegating(address account) {
    uint256 balance = balanceOf(account);
    bool isDelegatingVoting = getDelegatingVoting(account);
    bool isDelegatingProposition = getDelegatingProposition(account);
    uint72 dvb = getDelegatedVotingBalance(account);
    uint72 dpb = getDelegatedPropositionBalance(account);

    uint256 votingPower = getPowerCurrent(account, VOTING_POWER());
    uint256 propositionPower = getPowerCurrent(account, PROPOSITION_POWER());

    assert dvb == 0 && !isDelegatingVoting => votingPower == balance;
    assert dpb == 0 && !isDelegatingProposition => propositionPower == balance;
}

// wrong, user may delegate to himself/0 and the flag will be set true
rule selfDelegationCorrectness(address account) {
    bool isDelegatingVoting = getDelegatingVoting(account);
    bool isDelegatingProposition = getDelegatingProposition(account);
    address votingDelegate = getVotingDelegate(account);
    address propositionDelegate = getPropositionDelegate(account);

    assert votingDelegate == 0 || votingDelegate == account => isDelegatingVoting == false;
    assert propositionDelegate == 0 || propositionDelegate == account => isDelegatingProposition == false;

}
