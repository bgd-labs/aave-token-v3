/**

    Setup for writing rules for Aave Token v3 

*/

/**
    Public methods from the AaveTokenV3Harness.sol
*/

methods{
    totalSupply() returns (uint256) envfree
    balanceOf(address addr) returns (uint256) envfree
    transfer(address to, uint256 amount) returns (bool)
    transferFrom(address from, address to, uint256 amount) returns (bool)
    delegate(address delegatee)
    delegateByType(address delegatee, uint8 delegationType)
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

/**

    Constants

*/
// GovernancyType enum from the token contract
definition VOTING_POWER() returns uint8 = 0;
definition PROPOSITION_POWER() returns uint8 = 1;

definition DELEGATED_POWER_DIVIDER() returns uint256 = 10^10;

// 16000000 * 10^18 is the maximum supply of the AAVE token
definition MAX_DELEGATED_BALANCE() returns uint256 = 16000000 * 10^18 / DELEGATED_POWER_DIVIDER();

/**

    Function that normalizes (removes 10 least significant digits) a given param. 
    It mirrors the way delegated balances are stored in the token contract. Since the delegated
    balance is stored as a uint72 variable, delegated amounts (uint256()) are normalized.

*/

function normalize(uint256 amount) returns uint256 {
    return to_uint256(amount / DELEGATED_POWER_DIVIDER() * DELEGATED_POWER_DIVIDER());
}

function normalize_mathint(mathint amount) returns mathint {
    return to_uint256(amount / DELEGATED_POWER_DIVIDER() * DELEGATED_POWER_DIVIDER());
}
/**

    Testing correctness of delegate(). An example of a unit test

*/

rule delegateCorrectness(address bob) {
    env e;
    // delegate not to self or to zero
    require bob != e.msg.sender && bob != 0;

    uint256 bobDelegatedBalance = getDelegatedVotingBalance(bob);
    // avoid unrealistic delegated balance
    require(bobDelegatedBalance < MAX_DELEGATED_BALANCE());
    
    // verify that the sender doesn't already delegate to bob
    address delegateBefore = getVotingDelegate(e.msg.sender);
    require delegateBefore != bob;

    uint256 bobVotingPowerBefore = getPowerCurrent(bob, VOTING_POWER());
    uint256 delegatorBalance = balanceOf(e.msg.sender);

    delegate(e, bob);

    // test the delegate indeed has changed to bob
    address delegateAfter = getVotingDelegate(e.msg.sender);
    assert delegateAfter == bob;

    // test the delegate's new voting power
    uint256 bobVotingPowerAfter = getPowerCurrent(bob, VOTING_POWER());
    assert bobVotingPowerAfter == bobVotingPowerBefore + normalize(delegatorBalance);
}

/**

    Verify that only delegate functions can change someone's delegate.
    An example for a parametric rule.

*/

rule votingDelegateChanges(address alice, method f) {
    env e;
    calldataarg args;

    address aliceDelegateBefore = getVotingDelegate(alice);

    f(e, args);

    address aliceDelegateAfter = getVotingDelegate(alice);

    // only these four function may change the delegate of an address
    assert aliceDelegateAfter != aliceDelegateBefore =>
        f.selector == delegate(address).selector || 
        f.selector == delegateByType(address,uint8).selector ||
        f.selector == metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector ||
        f.selector == metaDelegateByType(address,address,uint8,uint256,uint8,bytes32,bytes32).selector;
}

/**

    A ghost variable that tracks the sum of all addresses' balances

*/
ghost mathint sumBalances {
    init_state axiom sumBalances == 0;
}

/**

    This hook updates the sumBalances ghost whenever any address balance is updated

*/
hook Sstore _balances[KEY address user].balance uint104 balance
    (uint104 old_balance) STORAGE {
        sumBalances = sumBalances - to_mathint(old_balance) + to_mathint(balance);
    }

/**

    Invariant: 
    sum of all addresses' balances should be always equal to the total supply of the token
    
*/
invariant totalSupplyEqualsBalances()
    sumBalances == totalSupply()









/** 
-----------------------------------------------------------------------------
 Contributions by Zarf 

 Discord: Zarf#7390 
 Twitter: https://twitter.com/zarfsec

 */


/**
    ghost variables which track the sum of all the delegated voting/proposition balances.
*/
ghost mathint sumDelegatedVotingBalances {
    init_state axiom sumDelegatedVotingBalances == 0;
}

ghost mathint sumDelegatedPropositionBalances {
    init_state axiom sumDelegatedPropositionBalances == 0;
}


/**
    This hook updates the delegated voting/proposition balances ghosts whenever any address' delegated voting/propisition balance is updated
*/
hook Sstore _balances[KEY address user].delegatedVotingBalance uint72 delegatedVotingBalance (uint72 old_DelegatedVotingBalance) STORAGE {
        sumDelegatedVotingBalances = sumDelegatedVotingBalances - to_mathint(old_DelegatedVotingBalance) + to_mathint(delegatedVotingBalance);
}

hook Sstore _balances[KEY address user].delegatedPropositionBalance uint72 delegatedPropositionBalance (uint72 old_DelegatedPropositionBalance) STORAGE {
        sumDelegatedPropositionBalances = sumDelegatedPropositionBalances - to_mathint(old_DelegatedPropositionBalance) + to_mathint(delegatedPropositionBalance);
}


function isVotingDelegator(address a) returns bool {
    return getDelegatingVoting(a) && getVotingDelegate(a) != a && getVotingDelegate(a) != 0;
}

function isPropositionDelegator(address a) returns bool {
    return getDelegatingProposition(a) && getPropositionDelegate(a) != a && getPropositionDelegate(a) != 0;
}


/**
    1. Ensure the zero address has no voting or proposition power
*/
invariant zeroAddressHasNoPower()
    getPowerCurrent(0, VOTING_POWER()) == 0 && getPowerCurrent(0, PROPOSITION_POWER()) == 0
{
    preserved {
        require balanceOf(0) == 0;
    }
}

/**
    2. Verify whether the total amount of delegated voting balances is preserved when transferring funds between two delegators.
*/
rule sumDelegatedVotingBalancesPreservedUponTransferBetweenDelegators(address a, address b) {

    require a != 0 && b != 0 && a != b;

    mathint sumDelegatedVotingBalancesBefore = sumDelegatedVotingBalances;

    env e;
    uint256 amount;
    require e.msg.sender == a;
    transfer(e, b, amount);

    mathint sumDelegatedVotingBalancesAfter = sumDelegatedVotingBalances;

    /**
        !!! NOT SURE IF REASONING IS CORRECT BUT:
        we take into account a small difference of +-1 instead of == 0 as the amount is converted to uint72 and looses precision.

        Therefore we cannot say sumDelegatedVotingBalancesBefore == sumDelegatedVotingBalancesAfter
    */
    assert isVotingDelegator(a) && isVotingDelegator(b) => 
        sumDelegatedVotingBalancesBefore - sumDelegatedVotingBalancesAfter <= 1;
}

/**
    3. Verify whether the total amount of delegated proposition balances is preserved when transferring funds between two delegators.
*/
rule sumDelegatedPropositionBalancesPreservedUponTransferBetweenDelegators(address a, address b) {

    require a != 0 && b != 0 && a != b;

    mathint sumDelegatedPropositionBalancesBefore = sumDelegatedPropositionBalances;

    env e;
    uint256 amount;
    require e.msg.sender == a;
    transfer(e, b, amount);

    mathint sumDelegatedPropositionBalancesAfter = sumDelegatedPropositionBalances;

    /** 
        !!! NOT SURE IF REASONING IS CORRECT BUT:
        we take into account a small difference of +-1 instead of == 0 as the amount is converted to uint72 and looses precision.

        Therefore we cannot say sumDelegatedVotingBalancesBefore == sumDelegatedVotingBalancesAfter
    */    
    assert isPropositionDelegator(a) && isPropositionDelegator(b) => 
        sumDelegatedPropositionBalancesBefore - sumDelegatedPropositionBalancesAfter <= 1;
}



/**
    4. Verify whether the voting power is correctly calculated depending on whether the user is delegating or not.
*/
rule votingPowerCalculationCorrectness(address a) {

    bool isDelegating = getDelegatingVoting(a);
    uint256 votingPower = getPowerCurrent(a, VOTING_POWER());

    assert isDelegating =>  votingPower == getDelegatedVotingBalance(a) * DELEGATED_POWER_DIVIDER();
    assert !isDelegating => votingPower == getBalance(a) + getDelegatedVotingBalance(a) * DELEGATED_POWER_DIVIDER();
}

/**
    5. Verify whether the proposition power is correctly calculated depending on whether the user is delegating or not.
*/
rule propositionPowerCalculationCorrectness(address a) {

    bool isDelegating = getDelegatingProposition(a);
    uint256 propositionPower = getPowerCurrent(a, PROPOSITION_POWER());

    assert isDelegating =>  propositionPower == getDelegatedPropositionBalance(a) * DELEGATED_POWER_DIVIDER();
    assert !isDelegating => propositionPower == getBalance(a) + getDelegatedPropositionBalance(a) * DELEGATED_POWER_DIVIDER();
}


/**
    6. Ensure a user without balance has not impact on the delegatee when starting to delegate voting power
*/
rule delegatingVotingPowerWithNoBalanceHasNoImpact(address delegator, address delegatee) {

    require delegator != 0 && delegatee != 0 && delegator != delegatee;
    uint256 votingPowerDelegateeBefore = getPowerCurrent(delegatee, VOTING_POWER());
    
    require getVotingDelegate(delegator) == delegatee;

    env e;
    uint256 amount;
    require e.msg.sender == delegator;
    delegateByType(e, delegatee, VOTING_POWER());

    uint256 votingPowerDelegateeAfter = getPowerCurrent(delegatee, VOTING_POWER());

    assert balanceOf(delegator) == 0 => votingPowerDelegateeAfter == votingPowerDelegateeBefore;
}

/**
    7. Ensure a user without balance has not impact on the delegatee when starting to delegate proposition power
*/
rule delegatingPropositionPowerWithNoBalanceHasNoImpact(address delegator, address delegatee) {

    require delegator != 0 && delegatee != 0 && delegator != delegatee;
    uint256 propositionPowerDelegateeBefore = getPowerCurrent(delegatee, PROPOSITION_POWER());

    require getPropositionDelegate(delegator) == delegatee;

    env e;
    uint256 amount;
    require e.msg.sender == delegator;
    delegateByType(e, delegatee, PROPOSITION_POWER());

    uint256 propositionPowerDelegateeAfter = getPowerCurrent(delegatee, PROPOSITION_POWER());

    assert balanceOf(delegator) == 0 => propositionPowerDelegateeAfter == propositionPowerDelegateeBefore;
}


/**
    8. Verifying voting power is properly updated when delegator stops delegating voting power.
*/
rule stopDelegatingVotingPowerCorrectness(address delegator, address delegatee) {
    env e;
    
    require getDelegatingVoting(delegator) && getVotingDelegate(delegator) == delegatee;
    // delegate not to self or to zero
    require delegator != delegatee && delegatee != 0;

    
    uint256 delegatorBalance = balanceOf(delegator);
    uint256 delegatorVotingPowerBefore = getPowerCurrent(delegator, VOTING_POWER());
    uint256 delegateeVotingPowerBefore = getPowerCurrent(delegatee, VOTING_POWER());

    require e.msg.sender == delegator;

    //delegate to address(0) is equivalent to stop delegating
    delegateByType(e, 0, VOTING_POWER());


    uint256 delegatorVotingPowerAfter = getPowerCurrent(delegator, VOTING_POWER());
    uint256 delegateeVotingPowerAfter = getPowerCurrent(delegatee, VOTING_POWER());

    //Verify delegator voting power is properly restored
    assert delegatorVotingPowerAfter == delegatorVotingPowerBefore + delegatorBalance;

    //Verify delegatee voting power is properly restored
    assert delegateeVotingPowerAfter == delegateeVotingPowerBefore - normalize(delegatorBalance);
}

/**
    9. Verifying proposition power is properly updated when delegator stops delegating proposition power.
*/
rule stopDelegatingPropositionPowerCorrectness(address delegator, address delegatee) {
    env e;
    
    require getDelegatingProposition(delegator) && getPropositionDelegate(delegator) == delegatee;
    // delegate not to self or to zero
    require delegator != delegatee && delegatee != 0;

    
    uint256 delegatorBalance = balanceOf(delegator);
    uint256 delegatorPropositionPowerBefore = getPowerCurrent(delegator, PROPOSITION_POWER());
    uint256 delegateePropositionPowerBefore = getPowerCurrent(delegatee, PROPOSITION_POWER());

    require e.msg.sender == delegator;

    //delegate to address(0) is equivalent to stop delegating
    delegateByType(e, 0, PROPOSITION_POWER());


    uint256 delegatorPropositionPowerAfter = getPowerCurrent(delegator, PROPOSITION_POWER());
    uint256 delegateePropositionPowerAfter = getPowerCurrent(delegatee, PROPOSITION_POWER());

    //Verify delegator proposition power is properly restored
    assert delegatorPropositionPowerAfter == delegatorPropositionPowerBefore + delegatorBalance;

    //Verify delegatee proposition power is properly restored
    assert delegateePropositionPowerAfter == delegateePropositionPowerBefore - normalize(delegatorBalance);
}


/**
    10. Verifying both voting and proposition power is properly updated when delegator stops delegating power.
*/
rule stopDelegatingPowerCorrectness(address delegator, address delegatee1, address delegatee2) {
    env e;
    
    require getDelegatingVoting(delegator) && getVotingDelegate(delegator) == delegatee1;
    require getDelegatingProposition(delegator) && getPropositionDelegate(delegator) == delegatee2;

    // delegate not to self or to zero
    require delegator != delegatee1 && delegatee1 != 0;
    require delegator != delegatee2 && delegatee2 != 0;

    
    uint256 delegatorBalance = balanceOf(delegator);
    uint256 delegatorVotingPowerBefore = getPowerCurrent(delegator, VOTING_POWER());
    uint256 delegatorPropositionPowerBefore = getPowerCurrent(delegator, PROPOSITION_POWER());
    uint256 delegatee1VotingPowerBefore = getPowerCurrent(delegatee1, VOTING_POWER());
    uint256 delegatee2PropositionPowerBefore = getPowerCurrent(delegatee2, PROPOSITION_POWER());


    require e.msg.sender == delegator;

    //delegate to address(0) is equivalent to stop delegating both proposition and voting power;
    delegate(e, 0);


    uint256 delegatorVotingPowerAfter = getPowerCurrent(delegator, VOTING_POWER());
    uint256 delegatorPropositionPowerAfter = getPowerCurrent(delegator, PROPOSITION_POWER());
    uint256 delegatee1VotingPowerAfter = getPowerCurrent(delegatee1, VOTING_POWER());
    uint256 delegatee2PropositionPowerAfter = getPowerCurrent(delegatee2, PROPOSITION_POWER());

    //Verify delegator voting power is properly restored
    assert delegatorVotingPowerAfter == delegatorVotingPowerBefore + delegatorBalance;
    //Verify delegator proposition power is properly restored
    assert delegatorPropositionPowerAfter == delegatorPropositionPowerBefore + delegatorBalance;

    //Verify delegatee voting power is properly restored
    assert delegatee1VotingPowerAfter == delegatee1VotingPowerBefore - normalize(delegatorBalance);
    //Verify delegatee proposition power is properly restored
    assert delegatee2PropositionPowerAfter == delegatee2PropositionPowerBefore - normalize(delegatorBalance);
}



/**
    11. Verifying voting power is properly updated when delegator is transfering balance while delegating.
*/
rule transferWithVotingPowerDelegationCorrectness(address delegator, address delegatee, address recipient) {
    
    //delegator is delegating to delegatee
    require getDelegatingVoting(delegator) && getVotingDelegate(delegator) == delegatee;
    //recipient is not delegating to reflect proper change in power
    require !getDelegatingVoting(recipient); 
    // delegate not to self or to zero
    require delegator != delegatee && delegatee != 0; 
    // transfer not to self or to zero
    require delegator != recipient && recipient != 0;
    // delegator is not the recipient
    require delegatee != recipient;

    uint256 delegatorBalanceBefore = balanceOf(delegator);
    uint256 delegatorVotingPowerBefore = getPowerCurrent(delegator, VOTING_POWER());
    uint256 delegateeVotingPowerBefore = getPowerCurrent(delegatee, VOTING_POWER());
    uint256 recipientVotingPowerBefore = getPowerCurrent(recipient, VOTING_POWER());

    env e;
    require e.msg.sender == delegator;
    uint256 amount;
    transfer(e, recipient, amount);

    uint256 delegatorBalanceAfter = balanceOf(delegator);
    uint256 delegatorVotingPowerAfter = getPowerCurrent(delegator, VOTING_POWER());
    uint256 delegateeVotingPowerAfter = getPowerCurrent(delegatee, VOTING_POWER());
    uint256 recipientVotingPowerAfter = getPowerCurrent(recipient, VOTING_POWER());

    //The power of the delegator does not change when transferring balance upon delegation
    assert delegatorVotingPowerAfter == delegatorVotingPowerBefore;

    //Verify power of delegatee is reduced
    assert delegateeVotingPowerAfter == delegateeVotingPowerBefore - normalize(delegatorBalanceBefore) + normalize(delegatorBalanceAfter);


    if (!getDelegatingVoting(recipient)) {
        //If recipient is not delegating, the power of the recipient must increase
        assert recipientVotingPowerAfter == recipientVotingPowerBefore + amount;
    } else {
        //If recipient is delegating, the power of the recipient must not change
        assert recipientVotingPowerAfter == recipientVotingPowerBefore;
    }
}


/**
    12. Verifying proposition power is properly updated when delegator is transfering balance while delegating.
*/
rule transferWithPropositionPowerDelegationCorrectness(address delegator, address delegatee, address recipient) {
    
    //delegator is delegating to delegatee
    require getDelegatingProposition(delegator) && getPropositionDelegate(delegator) == delegatee;
    //recipient is not delegating to reflect proper change in power
    require !getDelegatingProposition(recipient); 
    // delegate not to self or to zero
    require delegator != delegatee && delegatee != 0; 
    // transfer not to self or to zero
    require delegator != recipient && recipient != 0;
    // delegator is not the recipient
    require delegatee != recipient;

    uint256 delegatorBalanceBefore = balanceOf(delegator);
    uint256 delegatorPropositionPowerBefore = getPowerCurrent(delegator, PROPOSITION_POWER());
    uint256 delegateePropositionPowerBefore = getPowerCurrent(delegatee, PROPOSITION_POWER());
    uint256 recipientPropositionPowerBefore = getPowerCurrent(recipient, PROPOSITION_POWER());

    env e;
    require e.msg.sender == delegator;
    uint256 amount;
    transfer(e, recipient, amount);

    uint256 delegatorBalanceAfter = balanceOf(delegator);
    uint256 delegatorPropositionPowerAfter = getPowerCurrent(delegator, PROPOSITION_POWER());
    uint256 delegateePropositionPowerAfter = getPowerCurrent(delegatee, PROPOSITION_POWER());
    uint256 recipientPropositionPowerAfter = getPowerCurrent(recipient, PROPOSITION_POWER());

    //The power of the delegator does not change when transferring balance upon delegation
    assert delegatorPropositionPowerAfter == delegatorPropositionPowerBefore;

    //Verify power of delegatee is reduced
    assert delegateePropositionPowerAfter == delegateePropositionPowerBefore - normalize(delegatorBalanceBefore) + normalize(delegatorBalanceAfter);


    if (!getDelegatingProposition(recipient)) {
        //If recipient is not delegating, the power of the recipient must increase
        assert recipientPropositionPowerAfter == recipientPropositionPowerBefore + amount;
    } else {
        //If recipient is delegating, the power of the recipient must not change
        assert recipientPropositionPowerAfter == recipientPropositionPowerBefore;
    }
}


/**
    13. Verifying voting power increases/decreases while not being a voting delegatee yourself
*/
rule votingPowerChangesWhileNotBeingADelegatee(address a) {
    require a != 0;

    uint256 votingPowerBefore = getPowerCurrent(a, VOTING_POWER());
    uint256 balanceBefore = getBalance(a);
    bool isVotingDelegatorBefore = getDelegatingVoting(a);
    bool isVotingDelegateeBefore = getDelegatedVotingBalance(a) != 0;

    method f;
    env e;
    calldataarg args;
    f(e, args);

    uint256 votingPowerAfter = getPowerCurrent(a, VOTING_POWER());
    uint256 balanceAfter = getBalance(a);
    bool isVotingDelegatorAfter = getDelegatingVoting(a);
    bool isVotingDelegateeAfter = getDelegatedVotingBalance(a) != 0;

    require !isVotingDelegateeBefore && !isVotingDelegateeAfter;

    /** 
    If you're not a delegatee, your voting power only increases when
        1. You're not delegating and your balance increases
        2. You're delegating and stop delegating and your balanceBefore != 0
    */
    assert votingPowerBefore < votingPowerAfter <=> 
        (!isVotingDelegatorBefore && !isVotingDelegatorAfter && (balanceBefore < balanceAfter)) ||
        (isVotingDelegatorBefore && !isVotingDelegatorAfter && (balanceBefore != 0));

    /** 
    If you're not a delegatee, your voting power only decreases when
        1. You're not delegating and your balance decreases
        2. You're not delegating and start delegating and your balanceBefore != 0
    */
    assert votingPowerBefore > votingPowerAfter <=> 
        (!isVotingDelegatorBefore && !isVotingDelegatorAfter && (balanceBefore > balanceAfter)) ||
        (!isVotingDelegatorBefore && isVotingDelegatorAfter && (balanceBefore != 0));
}

/**
    14. Verifying porposition power increases/decreases while not being a proposition delegatee yourself
*/
rule propositionPowerChangesWhileNotBeingADelegatee(address a) {
    require a != 0;

    uint256 propositionPowerBefore = getPowerCurrent(a, PROPOSITION_POWER());
    uint256 balanceBefore = getBalance(a);
    bool isPropositionDelegatorBefore = getDelegatingProposition(a);
    bool isPropositionDelegateeBefore = getDelegatedPropositionBalance(a) != 0;

    method f;
    env e;
    calldataarg args;
    f(e, args);

    uint256 propositionPowerAfter = getPowerCurrent(a, PROPOSITION_POWER());
    uint256 balanceAfter = getBalance(a);
    bool isPropositionDelegatorAfter = getDelegatingProposition(a);
    bool isPropositionDelegateeAfter = getDelegatedPropositionBalance(a) != 0;

    require !isPropositionDelegateeBefore && !isPropositionDelegateeAfter;

    /** 
    If you're not a delegatee, your proposition power only increases when
        1. You're not delegating and your balance increases
        2. You're delegating and stop delegating and your balanceBefore != 0
    */
    assert propositionPowerBefore < propositionPowerAfter <=> 
        (!isPropositionDelegatorBefore && !isPropositionDelegatorAfter && (balanceBefore < balanceAfter)) ||
        (isPropositionDelegatorBefore && !isPropositionDelegatorAfter && (balanceBefore != 0));
    
    /** 
    If you're not a delegatee, your proposition power only decreases when
        1. You're not delegating and your balance decreases
        2. You're not delegating and start delegating and your balanceBefore != 0
    */
    assert propositionPowerBefore > propositionPowerAfter <=> 
        (!isPropositionDelegatorBefore && !isPropositionDelegatorBefore && (balanceBefore > balanceAfter)) ||
        (!isPropositionDelegatorBefore && isPropositionDelegatorAfter && (balanceBefore != 0));
}


/**
    15. Verifying voting power does not change when delegating the proposition power
*/
rule delegatingPropositionPowerDoesNotAlterVotingPower(address a, address b) {
    uint256 votingPowerBefore = getPowerCurrent(a, VOTING_POWER());

    env e;
    delegateByType(e, b, PROPOSITION_POWER());

    uint256 votingPowerAfter = getPowerCurrent(a, VOTING_POWER());

    assert votingPowerAfter == votingPowerBefore;
}

/**
    16. Verifying proposition power does not change when delegating the voting power
*/
rule delegatingVotingPowerDoesNotAlterPropositionPower(address a, address b) {
    uint256 propositionPowerBefore = getPowerCurrent(a, PROPOSITION_POWER());

    env e;
    delegateByType(e, b, VOTING_POWER());

    uint256 propositionPowerAfter = getPowerCurrent(a, PROPOSITION_POWER());

    assert propositionPowerAfter == propositionPowerBefore;
}


/**
    17. Verify token balances only change upon ERC20 transfer and transferFrom methods
*/
rule balanceChangesOnlyUponERC20Actions(address a) {

    uint256 balanceBefore = getBalance(a);

    method f;
    env e;
    calldataarg args;
    f(e, args);

    uint256 balanceAfter = getBalance(a);

    assert balanceAfter != balanceBefore =>
        f.selector == transfer(address,uint256).selector ||
        f.selector == transferFrom(address, address,uint256).selector;

}