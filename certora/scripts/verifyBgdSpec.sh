if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun certora/harness/AaveTokenV3Harness.sol:AaveTokenV3 \
    --verify AaveTokenV3:certora/specs/bgdSpec.spec \
    --rule $1 \
    --solc solc8.13 \
    --optimistic_loop \
    --send_only \
    --staging \
    --msg "AaveTokenV3:bgdSpec.spec $1"
 