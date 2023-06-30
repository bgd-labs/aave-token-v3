if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun certora/harness/AaveTokenV3Harness.sol:AaveTokenV3Harness \
    --verify AaveTokenV3Harness:certora/specs/delegate.spec \
    --packages openzeppelin-contracts=lib/openzeppelin-contracts \
    $RULE \
    --solc solc8.13 \
    --send_only \
    --optimistic_loop \
    --cloud \
    --msg "AaveTokenV3Harness:delegate.spec $1"
# --sanity

