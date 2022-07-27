if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun certora/harness/AaveTokenV3HarnessNew.sol:AaveTokenV3Harness \
    --verify AaveTokenV3Harness:certora/specs/delegate.spec \
    $RULE \
    --solc solc8.13 \
    --optimistic_loop \
    --send_only \
    --staging \
    --msg "AaveTokenV3:bgdSpec.spec $1"
 