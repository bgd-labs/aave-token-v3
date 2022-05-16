pragma solidity ^0.8.0;

contract BaseERC20Storage {
    struct DelegationAwareBalance {
        bool delegatingProposition;
        bool delegatingVoting;
        uint72 delegatedPropositionBalance;
        uint72 delegatedVotingBalance;
        uint104 balance;
    }

    mapping(address => DelegationAwareBalance) internal _balances;

    mapping(address => mapping(address => uint256)) internal _allowances;

    uint256 internal _totalSupply;

    string internal _name;
    string internal _symbol;

    // @dev DEPRECATED
    // kept for backwards compatibility with old storage layout
    uint8 private _decimals;
}
