| Name                                | Type                                                            | Slot | Offset | Bytes | Contract                        |
|-------------------------------------|-----------------------------------------------------------------|------|--------|-------|---------------------------------|
| _balances                           | mapping(address => struct BaseAaveToken.DelegationAwareBalance) | 0    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
| _allowances                         | mapping(address => mapping(address => uint256))                 | 1    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
| _totalSupply                        | uint256                                                         | 2    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
| _name                               | string                                                          | 3    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
| _symbol                             | string                                                          | 4    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
| ______DEPRECATED_OLD_ERC20_DECIMALS | uint8                                                           | 5    | 0      | 1     | src/AaveTokenV3.sol:AaveTokenV3 |
| lastInitializedRevision             | uint256                                                         | 6    | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
| ______gap                           | uint256[50]                                                     | 7    | 0      | 1600  | src/AaveTokenV3.sol:AaveTokenV3 |
| _nonces                             | mapping(address => uint256)                                     | 57   | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
| ______DEPRECATED_FROM_AAVE_V1       | uint256[3]                                                      | 58   | 0      | 96    | src/AaveTokenV3.sol:AaveTokenV3 |
| __DEPRECATED_DOMAIN_SEPARATOR       | bytes32                                                         | 61   | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
| ______DEPRECATED_FROM_AAVE_V2       | uint256[4]                                                      | 62   | 0      | 128   | src/AaveTokenV3.sol:AaveTokenV3 |
| _votingDelegatee                    | mapping(address => address)                                     | 66   | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
| _propositionDelegatee               | mapping(address => address)                                     | 67   | 0      | 32    | src/AaveTokenV3.sol:AaveTokenV3 |
