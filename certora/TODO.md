- [v] comment in the Harness file to explain the getters


- natspec. formatted like in openzeppelin specs
```

/**

*/

```
- [v] changed 'how to run' instructions to use munged

- add assert messages [last]

- [v] make sure properties.md on certora is identical to the main branch

- [v] delete the properties.md that i wrote

- [v] invariant delegationStateValid() and then requireInvariant in `delegateCorrectness`

- [v] voting power changes as a result of only specific calls (transfer, transferFrom, delegate, metadelegate, delegateByType)

- [v] transferAndTransferFrom are the same: do transfer and transferFrom at the same storage and check voting power transfer

- [v] delegationTypeIndependence => rewrite into more readable form (either both change)

- [v] transferDoesntChangeDelegationState: add charlie

- report: more about community, so many rules were submitted, so many were selected.