```diff
diff --git a/reports/AaveTokenV2_layout.md b/reports/AaveTokenV3_layout.md
index 0936f3f..964f7da 100644
--- a/reports/AaveTokenV2_layout.md
+++ b/reports/AaveTokenV3_layout.md
@@ -1,19 +1,16 @@
-| Name                             | Type                                                                                   | Slot | Offset | Bytes | Contract                                                      |
-|----------------------------------|----------------------------------------------------------------------------------------|------|--------|-------|---------------------------------------------------------------|
-| _balances                        | mapping(address => uint256)                                                            | 0    | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _allowances                      | mapping(address => mapping(address => uint256))                                        | 1    | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _totalSupply                     | uint256                                                                                | 2    | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _name                            | string                                                                                 | 3    | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _symbol                          | string                                                                                 | 4    | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _decimals                        | uint8                                                                                  | 5    | 0      | 1     | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| lastInitializedRevision          | uint256                                                                                | 6    | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| ______gap                        | uint256[50]                                                                            | 7    | 0      | 1600  | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _nonces                          | mapping(address => uint256)                                                            | 57   | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _votingSnapshots                 | mapping(address => mapping(uint256 => struct GovernancePowerDelegationERC20.Snapshot)) | 58   | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _votingSnapshotsCounts           | mapping(address => uint256)                                                            | 59   | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _aaveGovernance                  | contract ITransferHook                                                                 | 60   | 0      | 20    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| DOMAIN_SEPARATOR                 | bytes32                                                                                | 61   | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _votingDelegates                 | mapping(address => address)                                                            | 62   | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _propositionPowerSnapshots       | mapping(address => mapping(uint256 => struct GovernancePowerDelegationERC20.Snapshot)) | 63   | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _propositionPowerSnapshotsCounts | mapping(address => uint256)                                                            | 64   | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
-| _propositionPowerDelegates       | mapping(address => address)                                                            | 65   | 0      | 32    | lib/aave-token-v2/contracts/token/AaveTokenV2.sol:AaveTokenV2 |
+| Name                                | Type                                                            | Slot | Offset | Bytes | Contract                        |
+|-------------------------------------|-----------------------------------------------------------------|------|--------|-------|---------------------------------|
+| _balances                           | mapping(address => struct BaseAaveToken.DelegationAwareBalance) | 0    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
+| _allowances                         | mapping(address => mapping(address => uint256))                 | 1    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
+| _totalSupply                        | uint256                                                         | 2    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
+| _name                               | string                                                          | 3    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
+| _symbol                             | string                                                          | 4    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
+| ______DEPRECATED_OLD_ERC20_DECIMALS | uint8                                                           | 5    | 0      | 1     | src/AaveTokenV3.sol:AaveTokenV3 |
+| lastInitializedRevision             | uint256                                                         | 6    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
+| ______gap                           | uint256[50]                                                     | 7    | 0      | 1600  | src/AaveTokenV3.sol:AaveTokenV3 |
+| _nonces                             | mapping(address => uint256)                                     | 57   | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
+| ______DEPRECATED_FROM_AAVE_V1       | uint256[3]                                                      | 58   | 0      | 96    | src/AaveTokenV3.sol:AaveTokenV3 |
+| __DEPRECATED_DOMAIN_SEPARATOR       | bytes32                                                         | 61   | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
+| ______DEPRECATED_FROM_AAVE_V2       | uint256[4]                                                      | 62   | 0      | 128   | src/AaveTokenV3.sol:AaveTokenV3 |
+| _votingDelegatee                    | mapping(address => address)                                     | 66   | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
+| _propositionDelegatee               | mapping(address => address)                                     | 67   | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
```
