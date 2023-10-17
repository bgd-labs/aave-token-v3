
/*
    This is a specification file for the verification of delegation
    features of AaveTokenV3.sol smart contract using the Certora prover. 
    For more information, visit: https://www.certora.com/

    This file is run with scripts/verifyDelegate.sh
    On AaveTokenV3Harness.sol

    Sanity check results: https://prover.certora.com/output/67509/021f59de6995d82ecf18/?anonymousKey=84f18dc61532a37fabfd59655fe7fe43989f1a8e

*/

import "base.spec";


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
    mathint balance = balanceOf(account);
    bool isDelegatingVoting = getDelegatingVoting(account);
    bool isDelegatingProposition = getDelegatingProposition(account);
    uint72 dvb = getDelegatedVotingBalance(account);
    uint72 dpb = getDelegatedPropositionBalance(account);

    mathint votingPower = getPowerCurrent(account, VOTING_POWER());
    mathint propositionPower = getPowerCurrent(account, PROPOSITION_POWER());

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

    mathint alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    mathint bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());

    transferFrom(e, alice, bob, amount);

    mathint alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());

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

    mathint alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());

    transferFrom(e, alice, bob, amount);

    mathint alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());

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

    mathint aliceBalance = balanceOf(alice);
    mathint bobBalance = balanceOf(bob);

    mathint alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    mathint bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());

    delegate(e, bob);

    mathint alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());

    assert alicePowerAfter == alicePowerBefore - aliceBalance;
    assert bobPowerAfter == bobPowerBefore + (aliceBalance / DELEGATED_POWER_DIVIDER()) * DELEGATED_POWER_DIVIDER();
    assert getVotingDelegatee(alice) == bob;
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

    mathint aliceBalance = balanceOf(alice);
    mathint bobBalance = balanceOf(bob);

    mathint alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());

    delegate(e, bob);

    mathint alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());

    assert alicePowerAfter == alicePowerBefore - aliceBalance;
    assert bobPowerAfter == bobPowerBefore + (aliceBalance / DELEGATED_POWER_DIVIDER()) * DELEGATED_POWER_DIVIDER();
    assert getPropositionDelegatee(alice) == bob;
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
    address aliceDelegate = getVotingDelegatee(alice);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != bob && aliceDelegate != charlie;

    require isAliceDelegatingVoting && !isBobDelegatingVoting;

    mathint alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    // no delegation of anyone to Alice
    require alicePowerBefore == 0;

    mathint bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    mathint aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, VOTING_POWER());
    uint256 aliceBalanceBefore = balanceOf(alice);

    transferFrom(e, alice, bob, amount);

    mathint alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    mathint aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());
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
    address aliceDelegate = getPropositionDelegatee(alice);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != bob && aliceDelegate != charlie;

    require isAliceDelegatingProposition && !isBobDelegatingProposition;

    mathint alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    // no delegation of anyone to Alice
    require alicePowerBefore == 0;

    mathint bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    uint256 aliceBalanceBefore = balanceOf(alice);

    transferFrom(e, alice, bob, amount);

    mathint alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
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
    address aliceDelegate = getVotingDelegatee(alice);

    require isAliceDelegatingVoting && aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != charlie;

    mathint alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    mathint aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, VOTING_POWER());

    delegate(e, 0);

    mathint alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    mathint aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());

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
    address aliceDelegate = getPropositionDelegatee(alice);

    require isAliceDelegatingProposition && aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != charlie;

    mathint alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());

    delegate(e, 0);

    mathint alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());

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
    address aliceDelegate = getVotingDelegatee(alice);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != delegate2 && 
        delegate2 != 0 && delegate2 != charlie && aliceDelegate != charlie;

    require isAliceDelegatingVoting;

    mathint alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    mathint aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, VOTING_POWER());
    mathint delegate2PowerBefore = getPowerCurrent(delegate2, VOTING_POWER());

    delegate(e, delegate2);

    mathint alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    mathint aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());
    mathint delegate2PowerAfter = getPowerCurrent(delegate2, VOTING_POWER());
    address aliceDelegateAfter = getVotingDelegatee(alice);

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
    address aliceDelegate = getPropositionDelegatee(alice);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != delegate2 && 
        delegate2 != 0 && delegate2 != charlie && aliceDelegate != charlie;

    require isAliceDelegatingVoting;

    mathint alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    mathint delegate2PowerBefore = getPowerCurrent(delegate2, PROPOSITION_POWER());

    delegate(e, delegate2);

    mathint alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    mathint delegate2PowerAfter = getPowerCurrent(delegate2, PROPOSITION_POWER());
    address aliceDelegateAfter = getPropositionDelegatee(alice);

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
    address bobDelegate = getVotingDelegatee(bob);
    require bobDelegate != bob && bobDelegate != 0 && bobDelegate != alice && bobDelegate != charlie;

    require !isAliceDelegatingVoting && isBobDelegatingVoting;

    mathint alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    mathint bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    require bobPowerBefore == 0;
    mathint charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    mathint bobDelegatePowerBefore = getPowerCurrent(bobDelegate, VOTING_POWER());
    uint256 bobBalanceBefore = balanceOf(bob);

    transferFrom(e, alice, bob, amount);

    mathint alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    mathint bobDelegatePowerAfter = getPowerCurrent(bobDelegate, VOTING_POWER());
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
    address bobDelegate = getPropositionDelegatee(bob);
    require bobDelegate != bob && bobDelegate != 0 && bobDelegate != alice && bobDelegate != charlie;

    require !isAliceDelegating && isBobDelegating;

    mathint alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    require bobPowerBefore == 0;
    mathint charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint bobDelegatePowerBefore = getPowerCurrent(bobDelegate, PROPOSITION_POWER());
    uint256 bobBalanceBefore = balanceOf(bob);

    transferFrom(e, alice, bob, amount);

    mathint alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint bobDelegatePowerAfter = getPowerCurrent(bobDelegate, PROPOSITION_POWER());
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
    address aliceDelegate = getVotingDelegatee(alice);
    address bobDelegate = getVotingDelegatee(bob);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != bob && aliceDelegate != charlie;
    require bobDelegate != bob && bobDelegate != 0 && bobDelegate != alice && bobDelegate != charlie;
    require aliceDelegate != bobDelegate;

    mathint alicePowerBefore = getPowerCurrent(alice, VOTING_POWER());
    mathint bobPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, VOTING_POWER());
    mathint aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, VOTING_POWER());
    mathint bobDelegatePowerBefore = getPowerCurrent(bobDelegate, VOTING_POWER());
    uint256 aliceBalanceBefore = balanceOf(alice);
    uint256 bobBalanceBefore = balanceOf(bob);

    transferFrom(e, alice, bob, amount);

    mathint alicePowerAfter = getPowerCurrent(alice, VOTING_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, VOTING_POWER());
    mathint aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, VOTING_POWER());
    mathint bobDelegatePowerAfter = getPowerCurrent(bobDelegate, VOTING_POWER());
    uint256 aliceBalanceAfter = balanceOf(alice);
    uint256 bobBalanceAfter = balanceOf(bob);

    assert alicePowerAfter == alicePowerBefore;
    assert bobPowerAfter == bobPowerBefore;
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - normalize(aliceBalanceBefore) 
        + normalize(aliceBalanceAfter);

    mathint normalizedBalanceBefore = normalize(bobBalanceBefore);
    mathint normalizedBalanceAfter = normalize(bobBalanceAfter);
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
    address aliceDelegate = getPropositionDelegatee(alice);
    address bobDelegate = getPropositionDelegatee(bob);
    require aliceDelegate != alice && aliceDelegate != 0 && aliceDelegate != bob && aliceDelegate != charlie;
    require bobDelegate != bob && bobDelegate != 0 && bobDelegate != alice && bobDelegate != charlie;
    require aliceDelegate != bobDelegate;

    mathint alicePowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint bobPowerBefore = getPowerCurrent(bob, PROPOSITION_POWER());
    mathint charliePowerBefore = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint aliceDelegatePowerBefore = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    mathint bobDelegatePowerBefore = getPowerCurrent(bobDelegate, PROPOSITION_POWER());
    uint256 aliceBalanceBefore = balanceOf(alice);
    uint256 bobBalanceBefore = balanceOf(bob);

    transferFrom(e, alice, bob, amount);

    mathint alicePowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());
    mathint bobPowerAfter = getPowerCurrent(bob, PROPOSITION_POWER());
    mathint charliePowerAfter = getPowerCurrent(charlie, PROPOSITION_POWER());
    mathint aliceDelegatePowerAfter = getPowerCurrent(aliceDelegate, PROPOSITION_POWER());
    mathint bobDelegatePowerAfter = getPowerCurrent(bobDelegate, PROPOSITION_POWER());
    uint256 aliceBalanceAfter = balanceOf(alice);
    uint256 bobBalanceAfter = balanceOf(bob);

    assert alicePowerAfter == alicePowerBefore;
    assert bobPowerAfter == bobPowerBefore;
    assert aliceDelegatePowerAfter == aliceDelegatePowerBefore - normalize(aliceBalanceBefore) 
        + normalize(aliceBalanceAfter);

    mathint normalizedBalanceBefore = normalize(bobBalanceBefore);
    mathint normalizedBalanceAfter = normalize(bobBalanceAfter);
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

    address aliceVotingDelegateBefore = getVotingDelegatee(alice);
    address alicePropDelegateBefore = getPropositionDelegatee(alice);

    f(e, args);

    address aliceVotingDelegateAfter = getVotingDelegatee(alice);
    address alicePropDelegateAfter = getPropositionDelegatee(alice);

    // only these four function may change the delegate of an address
    assert aliceVotingDelegateAfter != aliceVotingDelegateBefore || alicePropDelegateBefore != alicePropDelegateAfter =>
        f.selector == sig:delegate(address).selector || 
        f.selector == sig:delegateByType(address,IGovernancePowerDelegationToken.GovernancePowerType).selector ||
        f.selector == sig:metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector ||
        f.selector == sig:metaDelegateByType(address,address,IGovernancePowerDelegationToken.GovernancePowerType,uint256,uint8,bytes32,bytes32).selector;
}

/*
    @Rule

    @Description:
        Verify that an account's voting and proposition power changes only as a result of a call to
        the delegation and transfer functions

    @Note:

    @Link:
*/
rule votingPowerChanges(address alice, method f) {
    env e;
    calldataarg args;

    uint aliceVotingPowerBefore = getPowerCurrent(alice, VOTING_POWER());
    uint alicePropPowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());

    f(e, args);

    uint aliceVotingPowerAfter = getPowerCurrent(alice, VOTING_POWER());
    uint alicePropPowerAfter = getPowerCurrent(alice, PROPOSITION_POWER());

    // only these four function may change the power of an address
    assert aliceVotingPowerAfter != aliceVotingPowerBefore || alicePropPowerAfter != alicePropPowerBefore =>
        f.selector == sig:delegate(address).selector || 
        f.selector == sig:delegateByType(address,IGovernancePowerDelegationToken.GovernancePowerType).selector ||
        f.selector == sig:metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector ||
        f.selector == sig:metaDelegateByType(address,address,IGovernancePowerDelegationToken.GovernancePowerType,uint256,uint8,bytes32,bytes32).selector ||
        f.selector == sig:transfer(address,uint256).selector ||
        f.selector == sig:transferFrom(address,address,uint256).selector;
}    

/*
    @Rule

    @Description:
        Verify that only delegate() and metaDelegate() may change both voting and
        proposition delegates of an account at once.
        nissan: I added also delegateByType() here.

    @Note:

    @Link:
*/
rule delegationTypeIndependence(address who, method f) filtered { f -> !f.isView } {
    address _delegateeV = getVotingDelegatee(who);
    address _delegateeP = getPropositionDelegatee(who);
	
    env e;
    calldataarg arg;
    f(e, arg);
	
    address delegateeV_ = getVotingDelegatee(who);
    address delegateeP_ = getPropositionDelegatee(who);
    assert _delegateeV != delegateeV_ && _delegateeP != delegateeP_ =>
        (f.selector == sig:delegate(address).selector ||
         f.selector == sig:metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector ||
         f.selector == sig:delegateByType(address,
                                  IGovernancePowerDelegationToken.GovernancePowerType).selector ||
         f.selector == sig:metaDelegateByType(address,address,
                                              IGovernancePowerDelegationToken.GovernancePowerType,
                                              uint256,uint8,bytes32,bytes32).selector
        ),
        "one delegatee type stays the same, unless delegate or delegateBySig was called";
}

/*
    @Rule

    @Description:
        Verifies that delegating twice to the same delegate changes the delegate's
        voting power only once.

    @Note:

    @Link:
*/
rule cantDelegateTwice(address _delegate) {
    env e;

    address delegateBeforeV = getVotingDelegatee(e.msg.sender);
    address delegateBeforeP = getPropositionDelegatee(e.msg.sender);
    require delegateBeforeV != _delegate && delegateBeforeV != e.msg.sender && delegateBeforeV != 0;
    require delegateBeforeP != _delegate && delegateBeforeP != e.msg.sender && delegateBeforeP != 0;
    require _delegate != e.msg.sender && _delegate != 0 && e.msg.sender != 0;
    require getDelegationMode(e.msg.sender) == FULL_POWER_DELEGATED();

    mathint votingPowerBefore = getPowerCurrent(_delegate, VOTING_POWER());
    mathint propPowerBefore = getPowerCurrent(_delegate, PROPOSITION_POWER());
    
    delegate(e, _delegate);
    
    mathint votingPowerAfter = getPowerCurrent(_delegate, VOTING_POWER());
    mathint propPowerAfter = getPowerCurrent(_delegate, PROPOSITION_POWER());

    delegate(e, _delegate);

    mathint votingPowerAfter2 = getPowerCurrent(_delegate, VOTING_POWER());
    mathint propPowerAfter2 = getPowerCurrent(_delegate, PROPOSITION_POWER());

    assert votingPowerAfter == votingPowerBefore + normalize(balanceOf(e.msg.sender));
    assert propPowerAfter == propPowerBefore + normalize(balanceOf(e.msg.sender));
    assert votingPowerAfter2 == votingPowerAfter && propPowerAfter2 == propPowerAfter;
}

/*
    @Rule

    @Description:
        transfer and transferFrom change voting/proposition power identically

    @Note:

    @Link:
*/
rule transferAndTransferFromPowerEquivalence(address bob, uint amount) {
    env e1;
    env e2;
    storage init = lastStorage;

    address alice;
    require alice == e1.msg.sender;

    uint aliceVotingPowerBefore = getPowerCurrent(alice, VOTING_POWER());
    uint alicePropPowerBefore = getPowerCurrent(alice, PROPOSITION_POWER());

    transfer(e1, bob, amount);

    uint aliceVotingPowerAfterTransfer = getPowerCurrent(alice, VOTING_POWER());
    uint alicePropPowerAfterTransfer = getPowerCurrent(alice, PROPOSITION_POWER());

    transferFrom(e2, alice, bob, amount) at init;

    uint aliceVotingPowerAfterTransferFrom = getPowerCurrent(alice, VOTING_POWER());
    uint alicePropPowerAfterTransferFrom = getPowerCurrent(alice, PROPOSITION_POWER());

    assert aliceVotingPowerAfterTransfer == aliceVotingPowerAfterTransferFrom &&
           alicePropPowerAfterTransfer == alicePropPowerAfterTransferFrom;

}







/* The following invariant says that the voting power of a user is as it should be.
   That is, the sum of all balances of users that delegate to him, plus his balance in case 
   that he is not delegating  */

// From VAULT spec
/*
invariant inv_sumAllBalance_eq_totalSupply()
    sumAllBalance() == to_mathint(totalSupply())
    filtered {f -> f.selector != sig:havoc_all().selector}
ghost sumAllBalance() returns mathint {
    init_state axiom sumAllBalance() == 0;
}
hook Sstore _balances[KEY address a] uint256 balance (uint256 old_balance) STORAGE {
  havoc sumAllBalance assuming sumAllBalance@new() == sumAllBalance@old() + balance - old_balance;
}
hook Sload uint256 balance _balances[KEY address a] STORAGE {
    require to_mathint(balance) <= sumAllBalance();
}
*/

/*
ghost mapping(address => bool) mirror_approvedSenders { 
    init_state axiom forall address a. mirror_approvedSenders[a] == false;
}
hook Sstore _approvedSenders[KEY address key] bool newVal (bool oldVal) STORAGE {
    mirror_approvedSenders[key] = newVal;
}
hook Sload bool val _approvedSenders[KEY address key] STORAGE {
    require(mirror_approvedSenders[key] == val);
}
*/

ghost mapping(address => mathint) sum_all_voting_delegated_power {
    init_state axiom forall address delegatee. sum_all_voting_delegated_power[delegatee] == 0;
}
ghost mapping(address => mathint) sum_all_proposition_delegated_power {
    init_state axiom forall address delegatee. sum_all_proposition_delegated_power[delegatee] == 0;
}

// =========================================================================
//   mirror_votingDelegatee
// =========================================================================
ghost mapping(address => address) mirror_votingDelegatee { 
    init_state axiom forall address a. mirror_votingDelegatee[a] == 0;
}
hook Sstore _votingDelegatee[KEY address delegator] address new_delegatee (address old_delegatee) STORAGE {
    mirror_votingDelegatee[delegator] = new_delegatee;
    if ((mirror_delegationMode[delegator]==FULL_POWER_DELEGATED() ||
         mirror_delegationMode[delegator]==VOTING_DELEGATED()) &&
        new_delegatee != old_delegatee) { // if a delegator changes his delegatee
        sum_all_voting_delegated_power[new_delegatee] =
            sum_all_voting_delegated_power[new_delegatee] + (mirror_balance[delegator]/(10^10)*(10^10));
        sum_all_voting_delegated_power[old_delegatee] = 
            sum_all_voting_delegated_power[old_delegatee] - (mirror_balance[delegator]/(10^10)*(10^10));
    }
}
hook Sload address val _votingDelegatee[KEY address delegator] STORAGE {
    require(mirror_votingDelegatee[delegator] == val);
}
invariant mirror_votingDelegatee_correct()
    forall address a.mirror_votingDelegatee[a] == getVotingDelegatee(a);


// =========================================================================
//   mirror_propositionDelegatee
// =========================================================================
ghost mapping(address => address) mirror_propositionDelegatee { 
    init_state axiom forall address a. mirror_propositionDelegatee[a] == 0;
}
hook Sstore _propositionDelegatee[KEY address delegator] address new_delegatee (address old_delegatee) STORAGE {
    mirror_propositionDelegatee[delegator] = new_delegatee;
    if ((mirror_delegationMode[delegator]==FULL_POWER_DELEGATED() ||
         mirror_delegationMode[delegator]==PROPOSITION_DELEGATED()) &&
        new_delegatee != old_delegatee) { // if a delegator changes his delegatee
        sum_all_proposition_delegated_power[new_delegatee] =
            sum_all_proposition_delegated_power[new_delegatee] + (mirror_balance[delegator]/(10^10)*(10^10));
        sum_all_proposition_delegated_power[old_delegatee] = 
            sum_all_proposition_delegated_power[old_delegatee] - (mirror_balance[delegator]/(10^10)*(10^10));
    }
}
hook Sload address val _propositionDelegatee[KEY address delegator] STORAGE {
    require(mirror_propositionDelegatee[delegator] == val);
}
invariant mirror_propositionDelegatee_correct()
    forall address a.mirror_propositionDelegatee[a] == getPropositionDelegatee(a);


// =========================================================================
//   mirror_delegationMode
// =========================================================================
ghost mapping(address => AaveTokenV3Harness.DelegationMode) mirror_delegationMode { 
    init_state axiom forall address a. mirror_delegationMode[a] ==
        AaveTokenV3Harness.DelegationMode.NO_DELEGATION;
}
hook Sstore _balances[KEY address a].delegationMode AaveTokenV3Harness.DelegationMode newVal (AaveTokenV3Harness.DelegationMode oldVal) STORAGE {
    mirror_delegationMode[a] = newVal;

    if ( (newVal==VOTING_DELEGATED() || newVal==FULL_POWER_DELEGATED())
         &&
         (oldVal!=VOTING_DELEGATED() && oldVal!=FULL_POWER_DELEGATED())
       ) { // if we start to delegate VOTING now
        sum_all_voting_delegated_power[mirror_votingDelegatee[a]] =
            sum_all_voting_delegated_power[mirror_votingDelegatee[a]] +
            (mirror_balance[a]/(10^10)*(10^10));
    }

    if ( (newVal==PROPOSITION_DELEGATED() || newVal==FULL_POWER_DELEGATED())
         &&
         (oldVal!=PROPOSITION_DELEGATED() && oldVal!=FULL_POWER_DELEGATED())
       ) { // if we start to delegate PROPOSITION now
        sum_all_proposition_delegated_power[mirror_propositionDelegatee[a]] =
            sum_all_proposition_delegated_power[mirror_propositionDelegatee[a]] +
            (mirror_balance[a]/(10^10)*(10^10));
    }
}
hook Sload AaveTokenV3Harness.DelegationMode val _balances[KEY address a].delegationMode STORAGE {
    require(mirror_delegationMode[a] == val);
}
invariant mirror_delegationMode_correct()
    forall address a.mirror_delegationMode[a] == getDelegationMode(a);



// =========================================================================
//   mirror_balance
// =========================================================================
ghost mapping(address => uint104) mirror_balance { 
    init_state axiom forall address a. mirror_balance[a] == 0;
}
hook Sstore _balances[KEY address a].balance uint104 balance (uint104 old_balance) STORAGE {
    mirror_balance[a] = balance;
    //sum_all_voting_delegated_power[a] = sum_all_voting_delegated_power[a] + balance - old_balance;
    // The code should be:
    // if a delegates to b, sum_all_voting_delegated_power[b] += the diff of balances of a
    if (a!=0 &&
        (mirror_delegationMode[a]==FULL_POWER_DELEGATED() ||
         mirror_delegationMode[a]==VOTING_DELEGATED() )
        )
        sum_all_voting_delegated_power[mirror_votingDelegatee[a]] =
            sum_all_voting_delegated_power[mirror_votingDelegatee[a]] +
            (balance/ (10^10) * (10^10)) - (old_balance/ (10^10) * (10^10)) ;

    if (a!=0 &&
        (mirror_delegationMode[a]==FULL_POWER_DELEGATED() ||
         mirror_delegationMode[a]==PROPOSITION_DELEGATED() )
        )
        sum_all_proposition_delegated_power[mirror_propositionDelegatee[a]] =
            sum_all_proposition_delegated_power[mirror_propositionDelegatee[a]] +
            (balance/ (10^10) * (10^10)) - (old_balance/ (10^10) * (10^10)) ;
}
hook Sload uint104 bal _balances[KEY address a].balance STORAGE {
    require(mirror_balance[a] == bal);
}
invariant mirror_balance_correct()
    forall address a.mirror_balance[a] == getBalance(a);




invariant inv_voting_power_correct(address user) 
    user != 0 =>
    (
     to_mathint(getPowerCurrent(user, VOTING_POWER()))
     ==
     sum_all_voting_delegated_power[user] +
     ( (mirror_delegationMode[user]==FULL_POWER_DELEGATED() ||
        mirror_delegationMode[user]==VOTING_DELEGATED())     ? 0 : mirror_balance[user])
    )
{
    preserved with (env e) {
        requireInvariant user_cant_voting_delegate_to_himself();
    }
}

invariant inv_proposition_power_correct(address user) 
    user != 0 =>
    (
     to_mathint(getPowerCurrent(user, PROPOSITION_POWER()))
     ==
     sum_all_proposition_delegated_power[user] +
     ( (mirror_delegationMode[user]==FULL_POWER_DELEGATED() ||
        mirror_delegationMode[user]==PROPOSITION_DELEGATED())     ? 0 : mirror_balance[user])
    )
{
    preserved with (env e) {
        requireInvariant user_cant_proposition_delegate_to_himself();
    }
}





rule no_function_changes_both_balance_and_delegation_state(method f, address bob) {
    env e;
    calldataarg args;

    require (bob != 0);

    uint256 bob_balance_before = balanceOf(bob);
    bool is_bob_delegating_voting_before = getDelegatingVoting(bob);
    address bob_delegatee_before = mirror_votingDelegatee[bob];

    f(e,args);

    uint256 bob_balance_after = balanceOf(bob);
    bool is_bob_delegating_voting_after = getDelegatingVoting(bob);
    address bob_delegatee_after = mirror_votingDelegatee[bob];

    assert (bob_balance_before != bob_balance_after =>
            (is_bob_delegating_voting_before==is_bob_delegating_voting_after &&
             bob_delegatee_before == bob_delegatee_after)
           );

    assert (bob_delegatee_before != bob_delegatee_after =>
            bob_balance_before == bob_balance_after
           );

    assert (is_bob_delegating_voting_before!=is_bob_delegating_voting_after =>
            bob_balance_before == bob_balance_after            
            );
  
}



invariant user_cant_voting_delegate_to_himself()
    forall address a. a!=0 => mirror_votingDelegatee[a] != a;

invariant user_cant_proposition_delegate_to_himself()
    forall address a. a!=0 => mirror_propositionDelegatee[a] != a;



//===================================================================================
//===================================================================================
// High-level rules that verify that a change in the balance (generated by any function)
// results in a correct change in the power.
//===================================================================================
//===================================================================================

/*
    @Rule

    @Description:
        Verify correct voting power after any change in (any user) balance.
        We consider the following case:
        - bob is the delegatee of alice1, and possibly of alice2. No other user delegates
        to bob.
        - bob may be delegating and may not.
        - We assume that the function that was call doesn't change the delegation state of neither
          bob, alice1 or alice2.

        We emphasize that we assume that no function alters both the balance of a user (Bob),
        and its delegation state (including the delegatee). We indeed check this property in the
        rule no_function_changes_both_balance_and_delegation_state().
        
    @Note:

    @Link:
*/
rule vp_change_in_balance_affect_power_DELEGATEE(method f,address bob,address alice1,address alice2) {
    env e;
    calldataarg args;
    require bob != 0; require alice1 != 0; require alice2 != 0;
    require (bob != alice1 && bob != alice2 && alice1 != alice2);

    uint256 bob_bal_before = balanceOf(bob);
    mathint bob_power_before = getPowerCurrent(bob, VOTING_POWER());
    bool is_bob_delegating_before = getDelegatingVoting(bob);

    uint256 alice1_bal_before = balanceOf(alice1);
    bool is_alice1_delegating_before = getDelegatingVoting(alice1);
    address alice1D_before = getVotingDelegatee(alice1); // alice1D == alice1_delegatee
    uint256 alice2_bal_before = balanceOf(alice2);
    bool is_alice2_delegating_before = getDelegatingVoting(alice2);
    address alice2D_before = getVotingDelegatee(alice2); // alice2D == alice2_delegatee

    // The following says that alice1 is delegating to bob, alice2 may do so, and no other
    // user may do so.
    require (is_alice1_delegating_before && alice1D_before == bob);
    require forall address a. (a!=alice1 && a!=alice2) =>
        (mirror_votingDelegatee[a] != bob ||
         (mirror_delegationMode[a]!=VOTING_DELEGATED() &&
          mirror_delegationMode[a]!=FULL_POWER_DELEGATED()
         )
        );

    requireInvariant user_cant_voting_delegate_to_himself();
    requireInvariant inv_voting_power_correct(alice1);
    requireInvariant inv_voting_power_correct(alice2);
    requireInvariant inv_voting_power_correct(bob);

    f(e,args);
    
    uint256 alice1_bal_after = balanceOf(alice1);
    mathint alice1_power_after = getPowerCurrent(alice1,VOTING_POWER());
    bool is_alice1_delegating_after = getDelegatingVoting(alice1);
    address alice1D_after = getVotingDelegatee(alice1); // alice1D == alice1_delegatee
    uint256 alice2_bal_after = balanceOf(alice2);
    mathint alice2_power_after = getPowerCurrent(alice2,VOTING_POWER());
    bool is_alice2_delegating_after = getDelegatingVoting(alice2);
    address alice2D_after = getVotingDelegatee(alice2); // alice2D == alice2_delegatee

    require (is_alice1_delegating_after && alice1D_after == bob);
    require forall address a. (a!=alice1 && a!=alice2) =>
        (mirror_votingDelegatee[a] != bob ||
         (mirror_delegationMode[a]!=VOTING_DELEGATED() &&
          mirror_delegationMode[a]!=FULL_POWER_DELEGATED()
         )
        );
    // No change in the delegation state of alice2
    require (is_alice2_delegating_before==is_alice2_delegating_after &&
             alice2D_before == alice2D_after);

    uint256 bob_bal_after = balanceOf(bob);
    mathint bob_power_after = getPowerCurrent(bob, VOTING_POWER());
    bool is_bob_delegating_after = getDelegatingVoting(bob);

    // No change in the delegation state of bob
    require (is_bob_delegating_before == is_bob_delegating_after);

    mathint alice1_diff = 
        (is_alice1_delegating_after && alice1D_after==bob) ?
        normalize(alice1_bal_after) - normalize(alice1_bal_before) : 0;

    mathint alice2_diff = 
        (is_alice2_delegating_after && alice2D_after==bob) ?
        normalize(alice2_bal_after) - normalize(alice2_bal_before) : 0;

    mathint bob_diff = bob_bal_after - bob_bal_before;
    
    assert
        !is_bob_delegating_after =>
        bob_power_after == bob_power_before + alice1_diff + alice2_diff + bob_diff;

    assert
        is_bob_delegating_after =>
        bob_power_after == bob_power_before + alice1_diff + alice2_diff;
}



/*
    @Rule

    @Description:
        Verify correct voting power after any change in (any user) balance.
        We consider the following case:
        - No user is delegating to bob.
        - bob may be delegating and may not.
        - We assume that the function that was call doesn't change the delegation state of bob.

        We emphasize that we assume that no function alters both the balance of a user (Bob),
        and its delegation state (including the delegatee). We indeed check this property in the
        rule no_function_changes_both_balance_and_delegation_state().
        
    @Note:

    @Link:
*/
rule vp_change_of_balance_affect_power_NON_DELEGATEE(method f, address bob) {
    env e;
    calldataarg args;
    require bob != 0;
    
    uint256 bob_bal_before = balanceOf(bob);
    mathint bob_power_before = getPowerCurrent(bob, VOTING_POWER());
    bool is_bob_delegating_before = getDelegatingVoting(bob);

    // The following says the no one delegates to bob
    require forall address a. 
        (mirror_votingDelegatee[a] != bob ||
         (mirror_delegationMode[a]!=VOTING_DELEGATED() &&
          mirror_delegationMode[a]!=FULL_POWER_DELEGATED()
         )
        );

    requireInvariant user_cant_voting_delegate_to_himself();
    requireInvariant inv_voting_power_correct(bob);

    f(e,args);
    
    require forall address a. 
        (mirror_votingDelegatee[a] != bob ||
         (mirror_delegationMode[a]!=VOTING_DELEGATED() &&
          mirror_delegationMode[a]!=FULL_POWER_DELEGATED()
         )
        );

    uint256 bob_bal_after = balanceOf(bob);
    mathint bob_power_after = getPowerCurrent(bob, VOTING_POWER());
    bool is_bob_delegating_after = getDelegatingVoting(bob);
    mathint bob_diff = bob_bal_after - bob_bal_before;

    require (is_bob_delegating_before == is_bob_delegating_after);
    
    assert !is_bob_delegating_after => bob_power_after==bob_power_before + bob_diff;
    assert is_bob_delegating_after => bob_power_after==bob_power_before;
}




/*
    @Rule

    @Description:
        Verify correct proposition power after any change in (any user) balance.
        We consider the following case:
        - bob is the delegatee of alice1, and possibly of alice2. No other user delegates
        to bob.
        - bob may be delegating and may not.
        - We assume that the function that was call doesn't change the delegation state of neither
          bob, alice1 or alice2.

        We emphasize that we assume that no function alters both the balance of a user (Bob),
        and its delegation state (including the delegatee). We indeed check this property in the
        rule no_function_changes_both_balance_and_delegation_state().
        
    @Note:

    @Link:
*/
rule pp_change_in_balance_affect_power_DELEGATEE(method f,address bob,address alice1,address alice2) {
    env e;
    calldataarg args;
    require bob != 0; require alice1 != 0; require alice2 != 0;
    require (bob != alice1 && bob != alice2 && alice1 != alice2);

    uint256 bob_bal_before = balanceOf(bob);
    mathint bob_power_before = getPowerCurrent(bob, PROPOSITION_POWER());
    bool is_bob_delegating_before = getDelegatingProposition(bob);

    uint256 alice1_bal_before = balanceOf(alice1);
    bool is_alice1_delegating_before = getDelegatingProposition(alice1);
    address alice1D_before = getPropositionDelegatee(alice1); // alice1D == alice1_delegatee
    uint256 alice2_bal_before = balanceOf(alice2);
    bool is_alice2_delegating_before = getDelegatingProposition(alice2);
    address alice2D_before = getPropositionDelegatee(alice2); // alice2D == alice2_delegatee

    // The following says that alice1 is delegating to bob, alice2 may do so, and no other
    // user may do so.
    require (is_alice1_delegating_before && alice1D_before == bob);
    require forall address a. (a!=alice1 && a!=alice2) =>
        (mirror_propositionDelegatee[a] != bob ||
         (mirror_delegationMode[a]!=PROPOSITION_DELEGATED() &&
          mirror_delegationMode[a]!=FULL_POWER_DELEGATED()
         )
        );

    requireInvariant user_cant_proposition_delegate_to_himself();
    requireInvariant inv_proposition_power_correct(alice1);
    requireInvariant inv_proposition_power_correct(alice2);
    requireInvariant inv_proposition_power_correct(bob);

    f(e,args);
    
    uint256 alice1_bal_after = balanceOf(alice1);
    mathint alice1_power_after = getPowerCurrent(alice1,PROPOSITION_POWER());
    bool is_alice1_delegating_after = getDelegatingProposition(alice1);
    address alice1D_after = getPropositionDelegatee(alice1); // alice1D == alice1_delegatee
    uint256 alice2_bal_after = balanceOf(alice2);
    mathint alice2_power_after = getPowerCurrent(alice2,PROPOSITION_POWER());
    bool is_alice2_delegating_after = getDelegatingProposition(alice2);
    address alice2D_after = getPropositionDelegatee(alice2); // alice2D == alice2_delegatee

    require (is_alice1_delegating_after && alice1D_after == bob);
    require forall address a. (a!=alice1 && a!=alice2) =>
        (mirror_propositionDelegatee[a] != bob ||
         (mirror_delegationMode[a]!=PROPOSITION_DELEGATED() &&
          mirror_delegationMode[a]!=FULL_POWER_DELEGATED()
         )
        );
    // No change in the delegation state of alice2
    require (is_alice2_delegating_before==is_alice2_delegating_after &&
             alice2D_before == alice2D_after);

    uint256 bob_bal_after = balanceOf(bob);
    mathint bob_power_after = getPowerCurrent(bob, PROPOSITION_POWER());
    bool is_bob_delegating_after = getDelegatingProposition(bob);

    // No change in the delegation state of bob
    require (is_bob_delegating_before == is_bob_delegating_after);

    mathint alice1_diff = 
        (is_alice1_delegating_after && alice1D_after==bob) ?
        normalize(alice1_bal_after) - normalize(alice1_bal_before) : 0;

    mathint alice2_diff = 
        (is_alice2_delegating_after && alice2D_after==bob) ?
        normalize(alice2_bal_after) - normalize(alice2_bal_before) : 0;

    mathint bob_diff = bob_bal_after - bob_bal_before;
    
    assert
        !is_bob_delegating_after =>
        bob_power_after == bob_power_before + alice1_diff + alice2_diff + bob_diff;

    assert
        is_bob_delegating_after =>
        bob_power_after == bob_power_before + alice1_diff + alice2_diff;
}



/*
    @Rule

    @Description:
        Verify correct proposition power after any change in (any user) balance.
        We consider the following case:
        - No user is delegating to bob.
        - bob may be delegating and may not.
        - We assume that the function that was call doesn't change the delegation state of bob.

        We emphasize that we assume that no function alters both the balance of a user (Bob),
        and its delegation state (including the delegatee). We indeed check this property in the
        rule no_function_changes_both_balance_and_delegation_state().
        
    @Note:

    @Link:
*/

rule pp_change_of_balance_affect_power_NON_DELEGATEE(method f, address bob) {
    env e;
    calldataarg args;
    require bob != 0;
    
    uint256 bob_bal_before = balanceOf(bob);
    mathint bob_power_before = getPowerCurrent(bob, PROPOSITION_POWER());
    bool is_bob_delegating_before = getDelegatingProposition(bob);

    // The following says the no one delegates to bob
    require forall address a. 
        (mirror_propositionDelegatee[a] != bob ||
         (mirror_delegationMode[a]!=PROPOSITION_DELEGATED() &&
          mirror_delegationMode[a]!=FULL_POWER_DELEGATED()
         )
        );

    requireInvariant user_cant_proposition_delegate_to_himself();
    requireInvariant inv_proposition_power_correct(bob);

    f(e,args);
    
    require forall address a. 
        (mirror_propositionDelegatee[a] != bob ||
         (mirror_delegationMode[a]!=PROPOSITION_DELEGATED() &&
          mirror_delegationMode[a]!=FULL_POWER_DELEGATED()
         )
        );

    uint256 bob_bal_after = balanceOf(bob);
    mathint bob_power_after = getPowerCurrent(bob, PROPOSITION_POWER());
    bool is_bob_delegating_after = getDelegatingProposition(bob);
    mathint bob_diff = bob_bal_after - bob_bal_before;

    require (is_bob_delegating_before == is_bob_delegating_after);
    
    assert !is_bob_delegating_after => bob_power_after==bob_power_before + bob_diff;
    assert is_bob_delegating_after => bob_power_after==bob_power_before;
}

