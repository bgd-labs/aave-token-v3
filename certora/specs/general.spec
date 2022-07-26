import "base.spec"

methods {
    totalDelegatedVotingBalance() returns (uint256) envfree
    totalDelegatedPropositionBalance() returns (uint256) envfree
}

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
        sumDelegatedProposition = 
            sumDelegatedProposition + to_mathint(balance) * DELEGATED_POWER_DIVIDER() - to_mathint(old_balance) *
            DELEGATED_POWER_DIVIDER();
    }

// try to rewrite using power.spec in aave-tokenv2 customer code
hook Sstore _balances[KEY address user].balance uint104 balance
    (uint104 old_balance) STORAGE {
        sumBalances = sumBalances + to_mathint(balance) - to_mathint(old_balance);
    }

hook Sload uint104 balance _balances[KEY address user].balance STORAGE {
    require balance <= sumBalances;
}

hook Sload uint72 balance _balances[KEY address user].delegatedPropositionBalance STORAGE {
    require balance <= sumDelegatedProposition;
}


invariant sumDelegatedPropositionCorrectness() totalDelegatedPropositionBalance() <= totalSupply()

invariant nonDelegatingBalance(address user)
    !getDelegatingProposition(user) => balanceOf(user) == getDelegatedPropositionBalance(user) {
        preserved transfer(address to, uint256 amount) with (env e)
            {
                require(getVotingDelegate(to) != user);
            }
    }

rule sumDelegatedBalances(method f) {
    env e;
    calldataarg args;

    uint256 total = totalSupply();
    mathint sumBalancesGhost = sumBalances;
    require totalSupply() <= AAVE_MAX_SUPPLY();
    // proved elsewhere
    require sumBalances == totalSupply();
    uint256 sumBalancesBefore = totalDelegatedPropositionBalance();
    require sumBalancesBefore * DELEGATED_POWER_DIVIDER() <= sumBalancesGhost;
    if (f.selector == delegate(address).selector) {
        address delegatee;
        uint256 balance = balanceOf(e.msg.sender);
        bool isDelegating = getDelegatingProposition(e.msg.sender);
        require !isDelegating => sumBalancesBefore * DELEGATED_POWER_DIVIDER() <= sumBalancesGhost - balance;
        delegate(e, delegatee);
    } else if (f.selector == delegateByType(address,uint8).selector) {
        address delegatee;
        uint256 balance = balanceOf(e.msg.sender);
        bool isDelegating = getDelegatingProposition(e.msg.sender);
        require !isDelegating => sumBalancesBefore * DELEGATED_POWER_DIVIDER() <= sumBalancesGhost - balance;
        delegateByType(e, delegatee, PROPOSITION_POWER());
    } else if (f.selector == metaDelegate(address,address,uint256,uint8,bytes32,bytes32).selector) {
        address delegator; address delegatee; uint256 deadline; uint8 v; bytes32 r; bytes32 s;
        uint256 balance = balanceOf(delegator);
        bool isDelegating = getDelegatingProposition(delegator);
        require !isDelegating => sumBalancesBefore * DELEGATED_POWER_DIVIDER() <= sumBalancesGhost - balance;
        metaDelegate(e, delegator, delegatee, deadline, v, r, s); 
    } else if (f.selector == metaDelegateByType(address,address,uint8,uint256,uint8,bytes32,bytes32).selector) {
        address delegator; address delegatee; uint256 deadline; uint8 v; bytes32 r; bytes32 s;
        uint256 balance = balanceOf(delegator);
        bool isDelegating = getDelegatingProposition(delegator);
        require !isDelegating => sumBalancesBefore * DELEGATED_POWER_DIVIDER() <= sumBalancesGhost - balance;
        // metaDelegate by Proposition type (1)
        metaDelegateByType(e, delegator, delegatee, PROPOSITION_POWER(), deadline, v, r, s);
    } else if (f.selector == transfer(address,uint256).selector) {
        address to;
        uint256 amount;
        uint256 balance = balanceOf(e.msg.sender);
        require balance < AAVE_MAX_SUPPLY();
        bool isDelegating = getDelegatingProposition(e.msg.sender);
        address toDelegate = getPropositionDelegate(to);
        require toDelegate != 0;
        uint256 toDelegatePower = getPowerCurrent(toDelegate, PROPOSITION_POWER());

        require !isDelegating => sumBalancesBefore * DELEGATED_POWER_DIVIDER() <= sumBalancesGhost - amount;
        require isDelegating => sumBalancesBefore * DELEGATED_POWER_DIVIDER() >= balance + toDelegatePower;
        transfer(e, to, amount);
    } else if (f.selector == transferFrom(address,address,uint256).selector) {
        address to; 
        address from;
        uint256 amount;
        uint256 balanceFromBefore = balanceOf(from);
        uint256 balanceToBefore = balanceOf(to);
        require balanceFromBefore <= AAVE_MAX_SUPPLY();
        bool isDelegating = getDelegatingProposition(from);
        address delegateFrom = getPropositionDelegate(from);
        uint256 votingPowerFromDelegateBefore = getPowerCurrent(delegateFrom, PROPOSITION_POWER());
        address delegateTo = getPropositionDelegate(to);
        uint256 votingPowerToDelegateBefore = getPowerCurrent(delegateTo, PROPOSITION_POWER());
        require !isDelegating => sumBalancesBefore * DELEGATED_POWER_DIVIDER() <= sumBalancesGhost - amount;
        require isDelegating => sumBalancesBefore * DELEGATED_POWER_DIVIDER() >= balanceFromBefore;
        transferFrom(e, from, to, amount);
        uint256 balanceFromAfter = balanceOf(from);
        uint256 balanceToAfter = balanceOf(to);
        uint256 votingPowerFromDelegateAfter = getPowerCurrent(delegateFrom, PROPOSITION_POWER());
        uint256 votingPowerToDelegateAfter = getPowerCurrent(delegateTo, PROPOSITION_POWER());
        uint256 normAmount = normalize(amount);
        uint256 votingPowerDelta = votingPowerToDelegateAfter - votingPowerToDelegateBefore;
        assert isDelegating => votingPowerDelta == normAmount || delegateFrom == delegateTo;
    }
    else {
        f(e, args);
    }
    uint256 sumBalancesAfter = totalDelegatedPropositionBalance();
    assert sumBalancesAfter * DELEGATED_POWER_DIVIDER() <= sumBalancesGhost;
    
}

// TODO: separate rules for transfers, see that the sum of balances stays the same

// sum of power for two addresses involved in f, doesn't change.
rule sumPowerCurrent(method f)