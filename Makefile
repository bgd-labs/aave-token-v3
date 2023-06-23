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

git-diff :
	@mkdir -p diffs
	@printf '%s\n%s\n%s\n' "\`\`\`diff" "$$(git diff --no-index --diff-algorithm=patience --ignore-space-at-eol ${before} ${after})" "\`\`\`" > diffs/${out}.md


storage-diff :
	forge inspect lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 storage-layout --pretty  > reports/AaveTokenV2_layout.md
	forge inspect src/AaveTokenV3.sol:AaveTokenV3 storage-layout --pretty > reports/AaveTokenV3_layout.md
	make git-diff before=reports/AaveTokenV2_layout.md after=reports/AaveTokenV3_layout.md out=AaveToken_v2_v3_layout_diff
