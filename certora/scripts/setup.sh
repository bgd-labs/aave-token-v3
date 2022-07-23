if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun certora/harness/AaveTokenV3Harness.sol:AaveTokenV3 \
    --verify AaveTokenV3:certora/specs/setup.spec \
    $RULE \
    --solc solc8.13 \
    --optimistic_loop \
    --send_only \
    --cloud \
    --msg "AaveTokenV3:setup.spec $1"
