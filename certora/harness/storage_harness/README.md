This harness replaces DelegationState enum with a simple uint8 in order
to prove invariants about delegation.

Certora prover has some limitation with writing hooks on an enum field
inside a `struct`, hence the change.