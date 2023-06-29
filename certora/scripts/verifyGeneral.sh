if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun certora/harness/AaveTokenV3HarnessStorage.sol:AaveTokenV3Harness \
    --verify AaveTokenV3Harness:certora/specs/general.spec \
    --packages openzeppelin-contracts=lib/openzeppelin-contracts \
    $RULE \
    --solc solc8.13 \
    --optimistic_loop \
    --send_only \
    --prover_args "-smt_bitVectorTheory true" \
    --cloud \
    --msg "AaveTokenV3:general.spec $1"

