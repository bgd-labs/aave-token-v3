/*

This spec is for reproducing particular storage splitter issues
in the prover.

*/

import "base.spec"

definition NO_DELEGATION() returns uint = 0;
definition VOTING_DELEGATED() returns uint = 1;
definition PROPOSITION_DELEGATED() returns uint = 2;
definition FULL_POWER_DELEGATED() returns uint = 3;

// 1 byte
definition DelegationState(uint256 packed) returns uint256 = 
    (packed & 0xff00000000000000000000000000000000000000000000000000000000000000) >> 248;

// definition DelegationState(uint256 packed) returns uint256 = 
//     (packed & 0xff);

function delegatingVotingState(uint state) returns bool {
    return state == VOTING_DELEGATED() || state == FULL_POWER_DELEGATED();
}

ghost mathint sumDelegatedProposition {
    init_state axiom sumDelegatedProposition == 0;
}

ghost mathint sumBalances {
    init_state axiom sumBalances == 0;
}


/*
    @Rule

    @Description:
        User's delegation flag is switched on iff user is delegating to an address
        other than his own own or 0

    @Notes:


    @Link:

*/
invariant delegateCorrectness(address user)
    ((getVotingDelegate(user) == user || getVotingDelegate(user) == 0) <=> !getDelegatingVoting(user))
    &&
    ((getPropositionDelegate(user) == user || getPropositionDelegate(user) == 0) <=> !getDelegatingProposition(user))
    {
        preserved {
            require getDelegationState(user) <= FULL_POWER_DELEGATED();
        }
    }
/*

Invariant that proves sum of all balances is equal to sum of delegated and 
undelegated balances.

1. Ghost to track delegation state of each acc
2. Ghost to track delegated balances sum
3. Ghost to track undelegated balances sum
4. Ghost to track balances of each account
5. On each write to balance, check the ghost for delegation state and update either non deleg or deleg
6. On each write to delegation flag, move the balance from deleg to non deleg or the other way around
*/

// 1.
ghost mapping(address => bool) isDelegatingVoting {
    init_state axiom forall address a. isDelegatingVoting[a] == false;
}

// 2.
ghost mathint sumDelegatedBalances {
    init_state axiom sumDelegatedBalances == 0;
}

// 3.
ghost mathint sumUndelegatedBalances {
    init_state axiom sumUndelegatedBalances == 0;
}

// 4.
ghost mapping(address => uint104) balances {
    init_state axiom forall address a. balances[a] == 0;
}

hook Sstore _balances[KEY address user].(offset 0) uint256 packed STORAGE {
    uint256 old_state = DelegationState(packed);
    uint256 new_state = DelegationState(packed);
    bool willDelegate = ((old_state == NO_DELEGATION() || old_state == PROPOSITION_DELEGATED()) &&
        (new_state == VOTING_DELEGATED() || new_state == FULL_POWER_DELEGATED()));
    bool wasDelegating = ((old_state == VOTING_DELEGATED() || old_state == FULL_POWER_DELEGATED()) &&
        (new_state == NO_DELEGATION() || new_state == PROPOSITION_DELEGATED()));
    sumUndelegatedBalances = willDelegate ? (sumUndelegatedBalances - balances[user]) : sumUndelegatedBalances;
    sumUndelegatedBalances = wasDelegating ? (sumUndelegatedBalances + balances[user]) : sumUndelegatedBalances;
    sumDelegatedBalances = willDelegate ? (sumDelegatedBalances + balances[user]) : sumDelegatedBalances;
    sumDelegatedBalances = wasDelegating ? (sumDelegatedBalances - balances[user]) : sumDelegatedBalances;
    
    // change the delegating state only if a change is stored

    isDelegatingVoting[user] = new_state == old_state
        ? isDelegatingVoting[user]
        : new_state == VOTING_DELEGATED() || new_state == FULL_POWER_DELEGATED();

}


hook Sstore _balances[KEY address user].balance uint104 balance (uint104 old_balance) STORAGE {
    balances[user] = balances[user] - old_balance + balance;
    sumDelegatedBalances = isDelegatingVoting[user] 
        ? sumDelegatedBalances + to_mathint(balance) - to_mathint(old_balance)
        : sumDelegatedBalances;
    sumUndelegatedBalances = !isDelegatingVoting[user] 
        ? sumUndelegatedBalances + to_mathint(balance) - to_mathint(old_balance)
        : sumUndelegatedBalances;
}

invariant sumOfBalancesCorrectness() sumDelegatedBalances + sumUndelegatedBalances == totalSupply()


rule whochanged(method f, address user) {
    env e;
    calldataarg args;

    bool testBefore = isDelegatingVoting[user];
    address v_delegate = getVotingDelegate(user);
    address p_delegate = getPropositionDelegate(user);
    uint8 stateBefore = getDelegationState(user);
    require testBefore == delegatingVotingState(stateBefore);

    f(e, args);
    bool testAfter = isDelegatingVoting[user];
    uint8 stateAfter = getDelegationState(user);
    address v_delegateAfter = getVotingDelegate(user);

    assert testBefore == testAfter;
}

rule testTransfer() {
    env e;
    address from; address to;
    uint amount;

    uint8 stateFromBefore = getDelegationState(from);
    uint8 stateToBefore = getDelegationState(to);
    require stateFromBefore <= FULL_POWER_DELEGATED() && stateToBefore <= FULL_POWER_DELEGATED();
    bool testFromBefore = isDelegatingVoting[from];
    bool testToBefore = isDelegatingVoting[to];
    //require !delegatingVotingState(stateFromBefore) && !delegatingVotingState(stateToBefore);

    transferFrom(e, from, to, amount);

    uint8 stateFromAfter = getDelegationState(from);
    uint8 stateToAfter = getDelegationState(to);
    bool testFromAfter = isDelegatingVoting[from];
    bool testToAfter = isDelegatingVoting[to];

    assert testFromBefore == testFromAfter && testToBefore == testToAfter;
}
