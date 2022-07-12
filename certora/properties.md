## functions summary

### internals

- \_delegationMoveByType internal: apply operation on proper delegation balance
- \_delegationMove: delegation move by type _voting_, delegation move by type _proposition_
- \_transferWithDelegation: delegation move with `-` op for `from`, delegation move with `+` op for `to`
- \_getDelegatedPowerByType: returns the voting/proposition power by type
- \_getDelegateeByType: returns the delegate address if user is delegating, or 0 if not
- \_updateDelegateeByType: updates the delegate for user. if delegate == user, then delegate is recorded as 0.
- \_updateDelegationFlagByType: updates the user's flag for delegating by type
- \_delegateByType: the whole delegation process - update voting power and flags

### externals
- delegateByType: call the internal
- delegate():  call the internal on both types
- getDelegateeByType(): call the internal
- getPowerCurrent(): (if not delegating ) user balance + delegated balance
- metaDelegateByType(): delegate voting power using a signature from the delegator
- metaDelegate: metaDelegateByType for both types

## ideas for properties

- transfer where from == to doesn't change delegation balances
- address 0 has no voting/prop power
- \_transferWithDelegation removes delegation from `from` but does nothing on `to` if it's 0.
    who can call this?
- delegation flag <=> delegatee != 0
- anyone can delegate to zero. which means they're forfeiting the voting power.


## properties for Aave Token v3 spec

-- on token transfer, the delegation balances change correctly for all cases:
from delegating, to delegating, both delegating, none delegating

-- delegating to 0 == delegating to self. which means the flags are set to false

-- the flags are updated properly after delegation

-- the delegated power is stored divided by 10^10. make sure this doesn't kill precision.

-- 