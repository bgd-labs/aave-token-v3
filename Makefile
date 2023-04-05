# include .env file and export its env vars
# (-include to ignore error if it does not exist)
-include .env

# deps
update:; forge update

# Build & test
build  :; forge build --sizes

.PHONY : test

# IMPORTANT It is highly probable that will be necessary to modify the --fork-block-number, depending on the test
test   :; forge test -vvv --rpc-url=${RPC_MAINNET} --fork-block-number ${FORK_BLOCK}
trace   :; forge test -vvvv --rpc-url=${RPC_MAINNET}
clean  :; forge clean
snapshot :; forge snapshot
