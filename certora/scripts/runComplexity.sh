certoraRun src/AaveTokenV3.sol:AaveTokenV3 \
    --verify AaveTokenV3:certora/specs/complexity.spec \
    --solc solc8.13 \
    --optimistic_loop \
    --staging \
    --msg "AaveTokenV3 complexity check"
 