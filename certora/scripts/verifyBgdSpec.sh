if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun src/AaveTokenV3.sol:AaveTokenV3 \
    --verify AaveTokenV3:certora/specs/bdgSpec.spec \
    --solc solc8.13 \
    --optimistic_loop \
    --rule $1 \
    --staging \
    --msg "AaveTokenV3:bgdSpec.spec $1"
 