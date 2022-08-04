if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun certora/harness/AaveTokenV3Harness.sol:AaveTokenV3Harness \
    --verify AaveTokenV3Harness:certora/specs/repro.spec \
    $RULE \
    --solc solc8.13 \
    --optimistic_loop \
    --settings -smt_bitVectorTheory=true \
    --send_only \
    --staging \
    --msg "AaveTokenV3:repro.spec $1"
 