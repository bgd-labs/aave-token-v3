// using DelegationAwareBalance from "./BaseAaveToken.sol";

// issues:
// for enum, just use 0 (voting) and 1 (proposition) or local definition
// for struct use harness that replaces reads and writes with solidity functions

methods{
    totalSupply() returns (uint256) envfree
    balanceOf(address addr) returns (uint256) envfree
    transfer(address to, uint256 amount) returns (bool)
    transferFrom(address from, address to, uint256 amount) returns (bool)

    delegate(address delegatee)
    metaDelegate(address, address, uint256, uint8, bytes32, bytes32)
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
definition DELEGATED_POWER_DIVIDER() returns uint256 = 10^10;

function normalize(uint256 amount) returns uint256 {
    return to_uint256(amount / DELEGATED_POWER_DIVIDER() * DELEGATED_POWER_DIVIDER());
}

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

/**
    Account1 and account2 are not delegating power
*/

rule vpTransferWhenBothNotDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    bool isBobDelegatingVoting = getDelegatingVoting(bob);

    require !isAliceDelegatingVoting && !isBobDelegatingVoting;

    uint256 alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());

    assert alicePowerAfter == alicePowerBefore - amount;
    assert bobPowerAfter == bobPowerBefore + amount;
    assert charliePowerAfter == charliePowerBefore;
}


rule ppTransferWhenBothNotDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingProposition = getDelegatingProposition(alice);
    // bool isAliceDelegatingProposition = getDelegatedProposition(alice);

    bool isBobDelegatingProposition = getDelegatingProposition(bob);
    // bool isBobDelegatingProposition = getDelegatedProposition(bob);

    require !isAliceDelegatingProposition && !isBobDelegatingProposition;

    uint256 alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());

    assert alicePowerAfter == alicePowerBefore - amount;
    assert bobPowerAfter == bobPowerBefore + amount;
    assert charliePowerAfter == charliePowerBefore;
}

rule vpDelegateWhenBothNotDelegating(address alice, address bob, address charlie) {
    env e;
    require alice == e.msg.sender;
    require alice != 0 && bob != 0 && charlie != 0;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    bool isBobDelegatingVoting = getDelegatingVoting(bob);

    require !isAliceDelegatingVoting && !isBobDelegatingVoting;

    uint256 aliceBalance = balanceOf(alice);
    uint256 bobBalance = balanceOf(bob);

    uint256 alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());

    delegate(e, bob);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());

    assert alicePowerAfter == alicePowerBefore - aliceBalance;
    assert bobPowerAfter == bobPowerBefore + (aliceBalance / DELEGATED_POWER_DIVIDER()) * DELEGATED_POWER_DIVIDER();
    assert getVotingDelegate(alice) == bob;
    assert charliePowerAfter == charliePowerBefore;
}

rule ppDelegateWhenBothNotDelegating(address alice, address bob, address charlie) {
    env e;
    require alice == e.msg.sender;
    require alice != 0 && bob != 0 && charlie != 0;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingProposition = getDelegatingProposition(alice);
    bool isBobDelegatingProposition = getDelegatingProposition(bob);

    require !isAliceDelegatingProposition && !isBobDelegatingProposition;

    uint256 aliceBalance = balanceOf(alice);
    uint256 bobBalance = balanceOf(bob);

    uint256 alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());

    delegate(e, bob);

    uint256 alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());

    assert alicePowerAfter == alicePowerBefore - aliceBalance;
    assert bobPowerAfter == bobPowerBefore + (aliceBalance / DELEGATED_POWER_DIVIDER()) * DELEGATED_POWER_DIVIDER();
    assert getPropositionDelegate(alice) == bob;
    assert charliePowerAfter == charliePowerBefore;
}

/**
    Account1 is delegating power to delegatee1, account2 is not delegating power to anybody
*/

// token transfer from alice to bob

rule vpTransferWhenOnlyOneIsDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    bool isBobDelegatingVoting = getDelegatingVoting(bob);
    address aliceDelegate = getVotingDelegate(alice);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != bob && aliceDelegate != charlie;

    require isAliceDelegatingVoting && !isBobDelegatingVoting;

    uint256 alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    // no delegation of anyone to Alice
    require alicePowerBefore == 0;

    uint256 bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, VOTING_POWER());

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());

    // still zero
    assert alicePowerBefore == alicePowerAfter;
    assert aliceDelegatePowerAfter == 
        aliceDelegatePowerBefore - normalize(amount);
    assert bobPowerAfter == bobPowerBefore + amount;
    assert charliePowerBefore == charliePowerAfter;
}

/**
before: 133160000000000
amount: 30900000000001
after: 102250000000000

*/ 

rule ppTransferWhenOnlyOneIsDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingProposition = getDelegatingProposition(alice);
    bool isBobDelegatingProposition = getDelegatingProposition(bob);
    address aliceDelegate = getPropositionDelegate(alice);

    require isAliceDelegatingProposition && !isBobDelegatingProposition;

    uint256 alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    // no delegation of anyone to Alice
    require alicePowerBefore == 0;

    uint256 bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());

    // still zero
    assert alicePowerBefore == alicePowerAfter;
    // this is the equation in the properties.md, but it's wrong when amount == 10 ^ 10
    // assert aliceDelegatePowerAfter == 
    //     aliceDelegatePowerBefore - (amount / DELEGATED_POWER_DIVIDER() * DELEGATED_POWER_DIVIDER());
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore;
    assert bobPowerAfter == bobPowerBefore + amount;
    assert charliePowerBefore == charliePowerAfter;
}

// After account1 will stop delegating his power to delegatee1
rule vpStopDelegatingWhenOnlyOneIsDelegating(address alice, address charlie) {
    env e;
    require alice != charlie;
    require alice == e.msg.sender;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    address aliceDelegate = getVotingDelegate(alice);

    require isAliceDelegatingVoting;

    uint256 alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, VOTING_POWER());

    delegate(e, 0);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());

    assert alicePowerAfter == alicePowerBefore + balanceOf(alice);
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - balanceOf(alice);
    assert charliePowerAfter == charliePowerBefore;
}

rule ppStopDelegatingWhenOnlyOneIsDelegating(address alice, address charlie) {
    env e;
    require alice != charlie;
    require alice == e.msg.sender;

    bool isAliceDelegatingProposition = getDelegatingProposition(alice);
    address aliceDelegate = getPropositionDelegate(alice);

    require isAliceDelegatingProposition;

    uint256 alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());

    delegate(e, 0);

    uint256 alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());

    assert alicePowerAfter == alicePowerBefore + balanceOf(alice);
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - balanceOf(alice);
    assert charliePowerAfter == charliePowerBefore;
}

rule vpChangeDelegateWhenOnlyOneIsDelegating(address alice, address delegate2, address charlie) {
    env e;
    require alice != charlie && alice != delegate2 && charlie != delegate2;
    require alice == e.msg.sender;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    address aliceDelegate = getVotingDelegate(alice);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != delegate2 && delegate2 != 0;

    require isAliceDelegatingVoting;

    uint256 alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, VOTING_POWER());
    uint256 delegate2PowerBefore = getPowerCurrent(delegate2, VOTING_POWER());

    delegate(e, delegate2);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());
    uint256 delegate2PowerAfter = getPowerCurrent(delegate2, VOTING_POWER());
    address aliceDelegateAfter = getVotingDelegate(alice);

    assert alicePowerBefore == alicePowerAfter;
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - normalize(balanceOf(alice));
    assert delegate2PowerAfter == delegate2PowerBefore + normalize(balanceOf(alice));
    assert aliceDelegateAfter == delegate2;
    assert charliePowerAfter == charliePowerBefore;
}

// Account1 not delegating power to anybody, account2 is delegating power to delegatee2

rule vpOnlyAccount2IsDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    bool isBobDelegatingVoting = getDelegatingVoting(bob);
    address bobDelegate = getVotingDelegate(bob);
    require bobDelegate != bob && bobDelegate != 0 && bobDelegate != alice && bobDelegate != charlie;

    require !isAliceDelegatingVoting && isBobDelegatingVoting;

    uint256 alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    require bobPowerBefore == 0;
    uint256 charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    uint256 bobDelegatePowerBefore = getPowerCurrent(bobDelegate, VOTING_POWER());

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    uint256 bobDelegatePowerAfter = getPowerCurrent(bobDelegate, VOTING_POWER());

    assert alicePowerAfter == alicePowerBefore - amount;
    assert bobPowerAfter == 0;
    assert bobDelegatePowerAfter == bobDelegatePowerBefore + normalize(amount);

    assert charliePowerAfter == charliePowerBefore;
}

//add for proposition

// Account1 is delegating power to delegatee1, account2 is delegating power to delegatee2
rule vpTransferWhenBothAreDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    bool isBobDelegatingVoting = getDelegatingVoting(bob);
    require isAliceDelegatingVoting && isBobDelegatingVoting;
    address aliceDelegate = getVotingDelegate(alice);
    address bobDelegate = getVotingDelegate(bob);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != bob && aliceDelegate != charlie;
    require bobDelegate != bob && bobDelegate != 0 && bobDelegate != alice && bobDelegate != charlie;
    require aliceDelegate != bobDelegate;

    uint256 alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, VOTING_POWER());
    uint256 bobDelegatePowerBefore = getPowerCurrent(bobDelegate, VOTING_POWER());

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());
    uint256 bobDelegatePowerAfter = getPowerCurrent(bobDelegate, VOTING_POWER());

    assert alicePowerAfter == alicePowerBefore;
    assert bobPowerAfter == bobPowerBefore;
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - normalize(amount);
    assert bobDelegatePowerAfter == bobDelegatePowerBefore + normalize (amount);
}

/***

aliceDelegate before: 0x2cd68cfcc800 = 49300000000000
bobDelegate before: 0x63ced5b7b800 = 109740000000000

transfer: alice->bob 246

aliceDelegate after: 0x2cd68cfcc800 = 49300000000000
bobDelegate after: 0x63cc81abd400 = 109730000000000

0x143ecf6488f6, delegatorBalanceAfter=0x143ecf648800

balbefore: 0x569c76526c00 = 95230000000000 = 9523
balAfter:0x569c76526b0a = 95229999999754 = 9522


*/