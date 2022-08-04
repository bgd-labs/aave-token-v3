# aave-token-v3

Here the spec has two hooks, one on the balance field and one is using offset 0.

Failed run when DelegationState is at the end of the struct.

https://prover.certora.com/output/67509/57057282fda3e2abefca/?anonymousKey=64c0e318e73e5c124906755f7ca1a092e1fda03e

Successful (but vacuous) run when DelegationState is at the start of the struct.

https://prover.certora.com/output/67509/1aaa7ae25105510ee937/?anonymousKey=dc6d124db879952c6809203f87dff0aad49d6d36