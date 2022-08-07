
/*
    This is a specification file for the verification of delegation
    features of AaveTokenV3.sol smart contract using the Certora prover. 
    For more information, visit: https://www.certora.com/

    This file is run with scripts/verifyDelegate.sh
    On AaveTokenV3Harness.sol

*/

import "base.spec"


/*
    @Rule

    @Description:
        If an account is not receiving delegation of power (one type) from anybody,
        and that account is not delegating that power to anybody, the power of that account
        must be equal to its token balance.

    @Note:

    @Link:
*/

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


/**
    Account1 and account2 are not delegating power
*/

/*
    @Rule

    @Description:
        Verify correct voting power on token transfers, when both accounts are not delegating

    @Note:

    @Link:
*/

rule vpTransferWhenBothNotDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    bool isBobDelegatingVoting = getDelegatingVoting(bob);

    // both accounts are not delegating
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

/*
    @Rule

    @Description:
        Verify correct proposition power on token transfers, when both accounts are not delegating

    @Note:

    @Link:
*/

rule ppTransferWhenBothNotDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingProposition = getDelegatingProposition(alice);
    bool isBobDelegatingProposition = getDelegatingProposition(bob);

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

/*
    @Rule

    @Description:
        Verify correct voting power after Alice delegates to Bob, when 
        both accounts were not delegating

    @Note:

    @Link:
*/

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

/*
    @Rule

    @Description:
        Verify correct proposition power after Alice delegates to Bob, when 
        both accounts were not delegating

    @Note:

    @Link:
*/

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

/*
    @Rule

    @Description:
        Verify correct voting power after a token transfer from Alice to Bob, when 
        Alice was delegating and Bob wasn't

    @Note:

    @Link:
*/

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
    uint256 aliceBalanceBefore = balanceOf(alice);

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());
    uint256 aliceBalanceAfter = balanceOf(alice);

    assert alicePowerBefore == alicePowerAfter;
    assert aliceDelegatePowerAfter == 
        aliceDelegatePowerBefore - normalize(aliceBalanceBefore) + normalize(aliceBalanceAfter);
    assert bobPowerAfter == bobPowerBefore + amount;
    assert charliePowerBefore == charliePowerAfter;
}

/*
    @Rule

    @Description:
        Verify correct proposition power after a token transfer from Alice to Bob, when 
        Alice was delegating and Bob wasn't

    @Note:

    @Link:
*/

rule ppTransferWhenOnlyOneIsDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegatingProposition = getDelegatingProposition(alice);
    bool isBobDelegatingProposition = getDelegatingProposition(bob);
    address aliceDelegate = getPropositionDelegate(alice);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != bob && aliceDelegate != charlie;

    require isAliceDelegatingProposition && !isBobDelegatingProposition;

    uint256 alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    // no delegation of anyone to Alice
    require alicePowerBefore == 0;

    uint256 bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    uint256 aliceBalanceBefore = balanceOf(alice);

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    uint256 aliceBalanceAfter = balanceOf(alice);

    // still zero
    assert alicePowerBefore == alicePowerAfter;
    assert aliceDelegatePowerAfter == 
        aliceDelegatePowerBefore - normalize(aliceBalanceBefore) + normalize(aliceBalanceAfter);
    assert bobPowerAfter == bobPowerBefore + amount;
    assert charliePowerBefore == charliePowerAfter;
}


/*
    @Rule

    @Description:
        Verify correct voting power after Alice stops delegating, when 
        Alice was delegating and Bob wasn't

    @Note:

    @Link:
*/
rule vpStopDelegatingWhenOnlyOneIsDelegating(address alice, address charlie) {
    env e;
    require alice != charlie;
    require alice == e.msg.sender;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    address aliceDelegate = getVotingDelegate(alice);

    require isAliceDelegatingVoting && aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != charlie;

    uint256 alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, VOTING_POWER());

    delegate(e, 0);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());

    assert alicePowerAfter == alicePowerBefore + balanceOf(alice);
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - normalize(balanceOf(alice));
    assert charliePowerAfter == charliePowerBefore;
}

/*
    @Rule

    @Description:
        Verify correct proposition power after Alice stops delegating, when 
        Alice was delegating and Bob wasn't

    @Note:

    @Link:
*/
rule ppStopDelegatingWhenOnlyOneIsDelegating(address alice, address charlie) {
    env e;
    require alice != charlie;
    require alice == e.msg.sender;

    bool isAliceDelegatingProposition = getDelegatingProposition(alice);
    address aliceDelegate = getPropositionDelegate(alice);

    require isAliceDelegatingProposition && aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != charlie;

    uint256 alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());

    delegate(e, 0);

    uint256 alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());

    assert alicePowerAfter == alicePowerBefore + balanceOf(alice);
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - normalize(balanceOf(alice));
    assert charliePowerAfter == charliePowerBefore;
}

/*
    @Rule

    @Description:
        Verify correct voting power after Alice delegates

    @Note:

    @Link:
*/
rule vpChangeDelegateWhenOnlyOneIsDelegating(address alice, address delegate2, address charlie) {
    env e;
    require alice != charlie && alice != delegate2 && charlie != delegate2;
    require alice == e.msg.sender;

    bool isAliceDelegatingVoting = getDelegatingVoting(alice);
    address aliceDelegate = getVotingDelegate(alice);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != delegate2 && 
        delegate2 != 0 && delegate2 != charlie && aliceDelegate != charlie;

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

/*
    @Rule

    @Description:
        Verify correct proposition power after Alice delegates

    @Note:

    @Link:
*/
rule ppChangeDelegateWhenOnlyOneIsDelegating(address alice, address delegate2, address charlie) {
    env e;
    require alice != charlie && alice != delegate2 && charlie != delegate2;
    require alice == e.msg.sender;

    bool isAliceDelegatingVoting = getDelegatingProposition(alice);
    address aliceDelegate = getPropositionDelegate(alice);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != delegate2 && 
        delegate2 != 0 && delegate2 != charlie && aliceDelegate != charlie;

    require isAliceDelegatingVoting;

    uint256 alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    uint256 delegate2PowerBefore = getPowerCurrent(delegate2, PROPOSITION_POWER());

    delegate(e, delegate2);

    uint256 alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    uint256 delegate2PowerAfter = getPowerCurrent(delegate2, PROPOSITION_POWER());
    address aliceDelegateAfter = getPropositionDelegate(alice);

    assert alicePowerBefore == alicePowerAfter;
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - normalize(balanceOf(alice));
    assert delegate2PowerAfter == delegate2PowerBefore + normalize(balanceOf(alice));
    assert aliceDelegateAfter == delegate2;
    assert charliePowerAfter == charliePowerBefore;
}

/*
    @Rule

    @Description:
        Verify correct voting power after Alice transfers to Bob, when only Bob was delegating

    @Note:

    @Link:
*/

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
    uint256 bobBalanceBefore = balanceOf(bob);

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    uint256 bobDelegatePowerAfter = getPowerCurrent(bobDelegate, VOTING_POWER());
    uint256 bobBalanceAfter = balanceOf(bob);

    assert alicePowerAfter == alicePowerBefore - amount;
    assert bobPowerAfter == 0;
    assert bobDelegatePowerAfter == bobDelegatePowerBefore - normalize(bobBalanceBefore) + normalize(bobBalanceAfter);

    assert charliePowerAfter == charliePowerBefore;
}

/*
    @Rule

    @Description:
        Verify correct proposition power after Alice transfers to Bob, when only Bob was delegating

    @Note:

    @Link:
*/

rule ppOnlyAccount2IsDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegating = getDelegatingProposition(alice);
    bool isBobDelegating = getDelegatingProposition(bob);
    address bobDelegate = getPropositionDelegate(bob);
    require bobDelegate != bob && bobDelegate != 0 && bobDelegate != alice && bobDelegate != charlie;

    require !isAliceDelegating && isBobDelegating;

    uint256 alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    require bobPowerBefore == 0;
    uint256 charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 bobDelegatePowerBefore = getPowerCurrent(bobDelegate, PROPOSITION_POWER());
    uint256 bobBalanceBefore = balanceOf(bob);

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 bobDelegatePowerAfter = getPowerCurrent(bobDelegate, PROPOSITION_POWER());
    uint256 bobBalanceAfter = balanceOf(bob);

    assert alicePowerAfter == alicePowerBefore - amount;
    assert bobPowerAfter == 0;
    assert bobDelegatePowerAfter == bobDelegatePowerBefore - normalize(bobBalanceBefore) + normalize(bobBalanceAfter);

    assert charliePowerAfter == charliePowerBefore;
}


/*
    @Rule

    @Description:
        Verify correct voting power after Alice transfers to Bob, when both Alice
        and Bob were delegating

    @Note:

    @Link:
*/
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
    uint256 aliceBalanceBefore = balanceOf(alice);
    uint256 bobBalanceBefore = balanceOf(bob);

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());
    uint256 bobDelegatePowerAfter = getPowerCurrent(bobDelegate, VOTING_POWER());
    uint256 aliceBalanceAfter = balanceOf(alice);
    uint256 bobBalanceAfter = balanceOf(bob);

    assert alicePowerAfter == alicePowerBefore;
    assert bobPowerAfter == bobPowerBefore;
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - normalize(aliceBalanceBefore) 
        + normalize(aliceBalanceAfter);

    uint256 normalizedBalanceBefore = normalize(bobBalanceBefore);
    uint256 normalizedBalanceAfter = normalize(bobBalanceAfter);
    assert bobDelegatePowerAfter == bobDelegatePowerBefore - normalizedBalanceBefore + normalizedBalanceAfter;
}

/*
    @Rule

    @Description:
        Verify correct proposition power after Alice transfers to Bob, when both Alice
        and Bob were delegating

    @Note:

    @Link:
*/
rule ppTransferWhenBothAreDelegating(address alice, address bob, address charlie, uint256 amount) {
    env e;
    require alice != bob && bob != charlie && alice != charlie;

    bool isAliceDelegating = getDelegatingProposition(alice);
    bool isBobDelegating = getDelegatingProposition(bob);
    require isAliceDelegating && isBobDelegating;
    address aliceDelegate = getPropositionDelegate(alice);
    address bobDelegate = getPropositionDelegate(bob);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != bob && aliceDelegate != charlie;
    require bobDelegate != bob && bobDelegate != 0 && bobDelegate != alice && bobDelegate != charlie;
    require aliceDelegate != bobDelegate;

    uint256 alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    uint256 bobDelegatePowerBefore = getPowerCurrent(bobDelegate, PROPOSITION_POWER());
    uint256 aliceBalanceBefore = balanceOf(alice);
    uint256 bobBalanceBefore = balanceOf(bob);

    transferFrom(e, alice, bob, amount);

    uint256 alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    uint256 bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    uint256 charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    uint256 aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    uint256 bobDelegatePowerAfter = getPowerCurrent(bobDelegate, PROPOSITION_POWER());
    uint256 aliceBalanceAfter = balanceOf(alice);
    uint256 bobBalanceAfter = balanceOf(bob);

    assert alicePowerAfter == alicePowerBefore;
    assert bobPowerAfter == bobPowerBefore;
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - normalize(aliceBalanceBefore) 
        + normalize(aliceBalanceAfter);

    uint256 normalizedBalanceBefore = normalize(bobBalanceBefore);
    uint256 normalizedBalanceAfter = normalize(bobBalanceAfter);
    assert bobDelegatePowerAfter == bobDelegatePowerBefore - normalizedBalanceBefore + normalizedBalanceAfter;
}

/*
    @Rule

    @Description:
        Verify that an account's delegate changes only as a result of a call to
        the delegation functions

    @Note:

    @Link:
*/
rule votingDelegateChanges(address alice, method f) {
    env e;
    calldataarg args;

    address aliceVotingDelegateBefore = getVotingDelegate(alice);
    address alicePropDelegateBefore = getPropositionDelegate(alice);

    f(e, args);

    address aliceVotingDelegateAfter = getVotingDelegate(alice);
    address alicePropDelegateAfter = getPropositionDelegate(alice);

    // only these four function may change the delegate of an address
    assert aliceVotingDelegateAfter != aliceVotingDelegateBefore || alicePropDelegateBefore != alicePropDelegateAfter =>
        f.selector == delegate(address).selector || 
        f.selector == delegateByType(address,uint8).selector ||
        f.selector == metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector ||
        f.selector == metaDelegateByType(address,address,uint8,uint256,uint8,bytes32,bytes32).selector;
}


/*
    @Rule

    @Description:
        Verify that only delegate() and metaDelegate() may change both voting and
        proposition delegates of an account at once.

    @Note:

    @Link:
*/
rule delegationTypeIndependence(address who, method f) filtered { f -> !f.isView } {
	address _delegateeV = getVotingDelegate(who);
	address _delegateeP = getPropositionDelegate(who);
	
	env e;
	calldataarg arg;
	f(e, arg);
	
	address delegateeV_ = getVotingDelegate(who);
	address delegateeP_ = getPropositionDelegate(who);
	assert (_delegateeV == delegateeV_  || _delegateeP == delegateeP_) || (
		f.selector == delegate(address).selector ||
		f.selector == metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector
	), "one delegatee type stays the same, unless delegate or delegateBySig was called";
}

rule cantDelegateTwice(address _delegate) {
    env e;

    address delegateBefore = getVotingDelegate(e.msg.sender);
    require delegateBefore != _delegate && delegateBefore != e.msg.sender && delegateBefore != 0;
    require _delegate != e.msg.sender && _delegate != 0 && e.msg.sender != 0;
    require getDelegationState(e.msg.sender) == FULL_POWER_DELEGATED();

    uint256 votingPowerBefore = getPowerCurrent(_delegate, VOTING_POWER());
    uint256 propPowerBefore = getPowerCurrent(_delegate, PROPOSITION_POWER());
    
    delegate(e, _delegate);
    
    uint256 votingPowerAfter = getPowerCurrent(_delegate, VOTING_POWER());
    uint256 propPowerAfter = getPowerCurrent(_delegate, PROPOSITION_POWER());

    delegate(e, _delegate);

    uint256 votingPowerAfter2 = getPowerCurrent(_delegate, VOTING_POWER());
    uint256 propPowerAfter2 = getPowerCurrent(_delegate, PROPOSITION_POWER());

    assert votingPowerAfter == votingPowerBefore + normalize(balanceOf(e.msg.sender));
    assert propPowerAfter == propPowerBefore + normalize(balanceOf(e.msg.sender));
    assert votingPowerAfter2 == votingPowerAfter && propPowerAfter2 == propPowerAfter;
}