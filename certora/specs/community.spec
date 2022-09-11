import "base.spec"

methods {
    ecrecoverWrapper(bytes32 digest, uint8 v, bytes32 r, bytes32 s) returns (address) envfree
    computeMetaDelegateHash(address delegator,  address delegatee, uint256 deadline, uint256 nonce) returns (bytes32) envfree
    computeMetaDelegateByTypeHash(address delegator,  address delegatee, uint8 delegationType, uint256 deadline, uint256 nonce) returns (bytes32) envfree
    _nonces(address addr) returns (uint256) envfree
    getNonce(address addr) returns (uint256) envfree
}

definition ZERO_ADDRESS() returns address = 0;

/**
    Integrity of permit function
    Successful permit function increases the nonce of owner by 1 and also changes the allowance of owner to spender

    Written by parth-15
*/
rule permitIntegrity() {
    env e;
    address owner;
    address spender;
    uint256 value;
    uint256 deadline;
    uint8 v;
    bytes32 r;
    bytes32 s;

    uint256 allowanceBefore = allowance(owner, spender);
    mathint nonceBefore = getNonce(owner);

    //checking this because function is using unchecked math and such a high nonce is unrealistic
    require nonceBefore < max_uint;

    permit(e, owner, spender, value, deadline, v, r, s);

    uint256 allowanceAfter = allowance(owner, spender);
    mathint nonceAfter = getNonce(owner);

    assert allowanceAfter == value, "permit increases allowance of owner to spender on success";
    assert nonceAfter == nonceBefore + 1, "successful call to permit function increases nonce of owner by 1";
}

/**
    The delegator can always revoke his voting power only by calling delegating functions 

    Written by Elpacos

*/
rule checkRevokingVotingPower(address someone, method f) {
    env e;
    calldataarg args;

    //store voting delegating state before
    bool delegatingStateBefore = getDelegatingVoting(someone);
    //transacction
    f(e, args);
    //store voting delegating state after
    bool delegatingStateAfter = getDelegatingVoting(someone);

    assert (delegatingStateBefore => (delegatingStateAfter || !delegatingStateAfter));
    //assert that any delagation granted can be rovoked or changed to another delegatee using delegate functions
    assert ((delegatingStateBefore &&  !delegatingStateAfter )=>
        f.selector == delegate(address).selector || 
        f.selector == delegateByType(address,uint8).selector ||
        f.selector == metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector ||
        f.selector == metaDelegateByType(address,address,uint8,uint256,uint8,bytes32,bytes32).selector);
}

/**
    The delegator can always revoke his proposition power only by calling delegating functions

    Written by Elpacos

*/
rule checkRevokingPropositionPower(address someone, method f) {
    env e;
    calldataarg args;

    //store proposition delegating state before
    bool delegatingStateBefore = getDelegatingProposition(someone);
    //transacction
    f(e, args);
    //store proposition delegating state after
    bool delegatingStateAfter = getDelegatingProposition(someone);

    assert (delegatingStateBefore => (delegatingStateAfter || !delegatingStateAfter));
    //assert that any delagation granted can be rovoked or changed to another delegatee using delegate functions
    assert ((delegatingStateBefore &&  !delegatingStateAfter )=>
        f.selector == delegate(address).selector || 
        f.selector == delegateByType(address,uint8).selector ||
        f.selector == metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector ||
        f.selector == metaDelegateByType(address,address,uint8,uint256,uint8,bytes32,bytes32).selector);
}

/**

    Address 0 has no voting power and no proposition power

    Written by JayP11
*/
invariant addressZeroNoPower()
  getPowerCurrent(0, VOTING_POWER()) == 0 && getPowerCurrent(0, PROPOSITION_POWER()) == 0 && balanceOf(0) == 0


/**
 * Check `metaDelegateByType` can only be called with a signed request.

   Written by kustosz
 */
rule metaDelegateByTypeOnlyCallableWithProperlySignedArguments(env e, address delegator, address delegatee, uint8 delegationType, uint256 deadline, uint8 v, bytes32 r, bytes32 s) {
    require ecrecoverWrapper(computeMetaDelegateByTypeHash(delegator, delegatee, delegationType, deadline, _nonces(delegator)), v, r, s) != delegator;
    metaDelegateByType@withrevert(e, delegator, delegatee, delegationType, deadline, v, r, s);
    assert lastReverted;
}

/**
 * Check that it's impossible to use the same arguments to call `metaDalegate` twice.

   Written by kustosz
 */
rule metaDelegateNonRepeatable(env e1, env e2, address delegator, address delegatee, uint256 deadline, uint8 v, bytes32 r, bytes32 s) {
    uint256 nonce = _nonces(delegator);
    bytes32 hash1 = computeMetaDelegateHash(delegator, delegatee, deadline, nonce);
    bytes32 hash2 = computeMetaDelegateHash(delegator, delegatee, deadline, nonce+1);
    // assume no hash collisions
    require hash1 != hash2;
    // assume first call is properly signed
    require ecrecoverWrapper(hash1, v, r, s) == delegator;
    // assume ecrecover is sane: cannot sign two different messages with the same (v,r,s)
    require ecrecoverWrapper(hash2, v, r, s) != ecrecoverWrapper(hash1, v, r, s);
    metaDelegate(e1, delegator, delegatee, deadline, v, r, s);
    metaDelegate@withrevert(e2, delegator, delegatee, deadline, v, r, s);
    assert lastReverted;
}

/**

    Verify that only delegate functions can change someone's delegate.

    Written by PeterisPrieditis

*/

rule votingDelegateChanges_updated(address alice, method f) {
    env e;
    calldataarg args;

    address aliceVotingDelegateBefore = getVotingDelegate(alice);
    address alicePropositionDelegateBefore = getPropositionDelegate(alice);

    f(e, args);

    address aliceVotingDelegateAfter = getVotingDelegate(alice);
    address alicePropositionDelegateAfter = getPropositionDelegate(alice);

    // only these four function may change the delegate of an address
    assert (aliceVotingDelegateAfter != aliceVotingDelegateBefore) ||  (alicePropositionDelegateBefore != alicePropositionDelegateAfter) =>
        f.selector == delegate(address).selector || 
        f.selector == delegateByType(address,uint8).selector ||
        f.selector == metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector ||
        f.selector == metaDelegateByType(address,address,uint8,uint256,uint8,bytes32,bytes32).selector;
}


/*
    Power of the previous delegate is removed when the delegatee delegates to another delegate

    Written by priyankabhanderi
*/
rule delegatingToAnotherUserRemovesPowerFromOldDelegatee(env e, address alice, address bob) {

    require e.msg.sender != ZERO_ADDRESS(); 
    require e.msg.sender != alice && e.msg.sender != bob;
    require alice != ZERO_ADDRESS() && bob != ZERO_ADDRESS();

    require getVotingDelegate(e.msg.sender) != alice;

    uint72 _votingBalance = getDelegatedVotingBalance(alice);

    delegateByType(e, alice, VOTING_POWER());

    assert getVotingDelegate(e.msg.sender) == alice;

    delegateByType(e, bob, VOTING_POWER());

    assert getVotingDelegate(e.msg.sender) == bob;
    uint72 votingBalance_ = getDelegatedVotingBalance(alice);
    assert alice != bob => votingBalance_ == _votingBalance;
}

/*

    Voting and proposition power changes only as a result of a subset of functions

    Written by top-sekret

*/

rule powerChanges(address alice, method f) {
    env e;
    calldataarg args;

    uint8 type;
    require type <= 1;
    uint256 powerBefore = getPowerCurrent(alice, type);

    f(e, args);

    uint256 powerAfter = getPowerCurrent(alice, type);

    assert powerBefore != powerAfter =>
        f.selector == delegate(address).selector ||
        f.selector == delegateByType(address, uint8).selector ||
        f.selector == metaDelegate(address, address, uint256, uint8, bytes32, bytes32).selector ||
        f.selector == metaDelegateByType(address, address, uint8, uint256, uint8, bytes32, bytes32).selector ||
        f.selector == transfer(address, uint256).selector ||
        f.selector == transferFrom(address, address, uint256).selector;
}


/*
    Changing a delegate of one type doesn't influence the delegate of the other type

    Written by top-sekret
*/
rule delegateIndependence(method f) {
    env e;

    uint8 type;
    require type <= 1;

    address delegateBefore = type == 1 ? getPropositionDelegate(e.msg.sender) : getVotingDelegate(e.msg.sender);

    delegateByType(e, _, 1 - type);

    address delegateAfter = type == 1 ? getPropositionDelegate(e.msg.sender) : getVotingDelegate(e.msg.sender);

    assert delegateBefore == delegateAfter;
}

/**
    Verifying voting power increases/decreases while not being a voting delegatee yourself

    Written by Zarfsec
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
    Verifying proposition power increases/decreases while not being a proposition delegatee yourself

    Written by Zarfsec
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

