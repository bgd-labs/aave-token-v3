import "base.spec"

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