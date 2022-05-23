// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {VersionedInitializable} from "./utils/VersionedInitializable.sol";

import {IGovernancePowerDelegationToken} from "./interfaces/IGovernancePowerDelegationToken.sol";
import {BaseAaveTokenV2} from "./BaseAaveTokenV2.sol";
import {MathUtils} from "./utils/MathUtils.sol";

contract AaveTokenV3 is BaseAaveTokenV2, IGovernancePowerDelegationToken {
    mapping(address => address) internal _votingDelegateeV2;
    mapping(address => address) internal _propositionDelegateeV2;

    uint256 public constant DELEGATED_POWER_DIVIDER = 10**10;

    bytes32 public constant DELEGATE_BY_TYPE_TYPEHASH = keccak256(
        "DelegateByType(address owner,address delegatee,GovernancePowerType delegationType,uint256 nonce,uint256 deadline)"
    );
    bytes32 public constant DELEGATE_TYPEHASH = keccak256(
        "Delegate(address owner,address delegatee,uint256 nonce,uint256 deadline)"
    );

    function _delegationMoveByType(
        uint104 userBalanceBefore,
        uint104 userBalanceAfter,
        address delegatee,
        GovernancePowerType delegationType,
        function(uint72, uint72) returns (uint72) operation
    ) internal {
        if (delegatee == address(0)) return;

        uint72 delegationDelta = uint72(
            (userBalanceBefore / DELEGATED_POWER_DIVIDER) -
                (userBalanceAfter / DELEGATED_POWER_DIVIDER)
        );
        if (delegationDelta == 0) return;

        if (delegationType == GovernancePowerType.VOTING) {
            _balances[delegatee].delegatedVotingBalance = operation(
                _balances[delegatee].delegatedVotingBalance,
                delegationDelta
            );
        } else {
            _balances[delegatee].delegatedPropositionBalance = operation(
                _balances[delegatee].delegatedPropositionBalance,
                delegationDelta
            );
        }
        //TODO: emit DelegatedPowerChanged maybe;
    }

    function _delegationMove(
        address user,
        DelegationAwareBalance memory userState,
        uint104 balanceBefore,
        uint104 balanceAfter,
        function(uint72, uint72) returns (uint72) operation
    ) internal {
        _delegationMoveByType(
            balanceBefore,
            balanceAfter,
            _getDelegateeByType(user, userState, GovernancePowerType.VOTING),
            GovernancePowerType.VOTING,
            operation
        );
        _delegationMoveByType(
            balanceBefore,
            balanceAfter,
            _getDelegateeByType(
                user,
                userState,
                GovernancePowerType.PROPOSITION
            ),
            GovernancePowerType.PROPOSITION,
            operation
        );
    }

    function _transferWithDelegation(
        address from,
        address to,
        uint256 amount
    ) internal override {
        if (from == to) {
            return;
        }

        if (from != address(0)) {
            DelegationAwareBalance memory fromUserState = _balances[from];
            require(
                fromUserState.balance >= amount,
                "ERC20: transfer amount exceeds balance"
            );

            uint104 fromBalanceAfter;
            unchecked {
                //TODO: in general we don't need to check cast to uint104 because we know that it's less then balance from require
                fromBalanceAfter = fromUserState.balance - uint104(amount);
            }
            _balances[from].balance = fromBalanceAfter;
            if (
                fromUserState.delegatingProposition ||
                fromUserState.delegatingVoting
            )
                _delegationMove(
                    from,
                    fromUserState,
                    fromUserState.balance,
                    fromBalanceAfter,
                    MathUtils.minus
                );
        }

        if (to != address(0)) {
            DelegationAwareBalance memory toUserState = _balances[to];
            uint104 toBalanceBefore = toUserState.balance;
            toUserState.balance = toBalanceBefore + uint104(amount); // TODO: check overflow?
            _balances[to] = toUserState;

            if (
                toUserState.delegatingVoting ||
                toUserState.delegatingProposition
            ) {
                _delegationMove(
                    to,
                    toUserState,
                    toUserState.balance,
                    toBalanceBefore,
                    MathUtils.plus
                );
            }
        }
    }

    function _getDelegatedPowerByType(
        DelegationAwareBalance memory userState,
        GovernancePowerType delegationType
    ) internal pure returns (uint72) {
        return
            delegationType == GovernancePowerType.VOTING
                ? userState.delegatedVotingBalance
                : userState.delegatedPropositionBalance;
    }

    function _getDelegateeByType(
        address user,
        DelegationAwareBalance memory userState,
        GovernancePowerType delegationType
    ) internal view returns (address) {
        if (delegationType == GovernancePowerType.VOTING) {
            return
                userState.delegatingVoting
                    ? _votingDelegateeV2[user]
                    : address(0);
        }
        return
            userState.delegatingProposition
                ? _propositionDelegateeV2[user]
                : address(0);
    }

    function _updateDelegateeByType(
        address user,
        GovernancePowerType delegationType,
        address _newDelegatee
    ) internal {
        address newDelegatee = _newDelegatee == user
            ? address(0)
            : _newDelegatee;
        if (delegationType == GovernancePowerType.VOTING) {
            _votingDelegateeV2[user] = newDelegatee;
        } else {
            _propositionDelegateeV2[user] = newDelegatee;
        }
    }

    function _updateDelegationFlagByType(
        DelegationAwareBalance memory userState,
        GovernancePowerType delegationType,
        bool willDelegate
    ) internal pure returns (DelegationAwareBalance memory) {
        if (delegationType == GovernancePowerType.VOTING) {
            userState.delegatingVoting = willDelegate;
        } else {
            userState.delegatingProposition = willDelegate;
        }
        return userState;
    }

    function _delegateByType(
        address user,
        address _delegatee,
        GovernancePowerType delegationType
    ) internal {
        //we consider to 0x0 as delegation to self
        address delegatee = _delegatee == user ? address(0) : _delegatee;

        DelegationAwareBalance memory userState = _balances[user];
        address currentDelegatee = _getDelegateeByType(
            user,
            userState,
            delegationType
        );
        if (delegatee == currentDelegatee) return;

        bool delegatingNow = currentDelegatee != address(0);
        bool willDelegateAfter = delegatee != address(0);

        if (delegatingNow) {
            _delegationMoveByType(
                userState.balance,
                0,
                currentDelegatee,
                delegationType,
                MathUtils.minus
            );
        }
        if (willDelegateAfter) {
            _updateDelegateeByType(user, delegationType, delegatee);
            _delegationMoveByType(
                userState.balance,
                0,
                delegatee,
                delegationType,
                MathUtils.plus
            );
        }

        if (willDelegateAfter != delegatingNow) {
            _balances[user] = _updateDelegationFlagByType(
                userState,
                delegationType,
                willDelegateAfter
            );
        }

        emit DelegateChanged(user, delegatee, delegationType);
    }

    function delegateByType(
        address delegatee,
        GovernancePowerType delegationType
    ) external virtual override {
        _delegateByType(msg.sender, delegatee, delegationType);
    }

    /**
     * @dev delegates all the powers to a specific user
     * @param delegatee the user to which the power will be delegated
     **/
    function delegate(address delegatee) external override {
        _delegateByType(msg.sender, delegatee, GovernancePowerType.VOTING);
        _delegateByType(msg.sender, delegatee, GovernancePowerType.PROPOSITION);
    }

    function getDelegateeByType(
        address delegator,
        GovernancePowerType delegationType
    ) external view override returns (address) {
        return
            _getDelegateeByType(
                delegator,
                _balances[delegator],
                delegationType
            );
    }

    function getPowerCurrent(address user, GovernancePowerType delegationType)
        external
        view
        override
        returns (uint256)
    {
        DelegationAwareBalance memory userState = _balances[user];
        uint256 userOwnPower = (delegationType == GovernancePowerType.VOTING &&
            !userState.delegatingVoting) ||
            (delegationType == GovernancePowerType.PROPOSITION &&
                !userState.delegatingProposition)
            ? _balances[user].balance
            : 0;
        uint256 userDelegatedPower = _getDelegatedPowerByType(
            userState,
            delegationType
        ) * DELEGATED_POWER_DIVIDER;
        return userOwnPower + userDelegatedPower;
    }

    function metaDelegateByType(
        address owner,
        address delegatee,
        GovernancePowerType delegationType,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external override {
        require(owner != address(0), "INVALID_OWNER");
        //solium-disable-next-line
        require(block.timestamp <= deadline, "INVALID_EXPIRATION");
        uint256 currentValidNonce = _nonces[owner];
        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                DOMAIN_SEPARATOR,
                keccak256(
                    abi.encode(
                        DELEGATE_BY_TYPE_TYPEHASH,
                        owner,
                        delegate,
                        delegationType,
                        currentValidNonce,
                        deadline
                    )
                )
            )
        );

        require(owner == ecrecover(digest, v, r, s), "INVALID_SIGNATURE");
    unchecked {
        // does not make sense to check because it's not realistic to reach uint256.max in nonce
        _nonces[owner] = currentValidNonce + 1;
    }
        _delegateByType(owner, delegatee, delegationType);
    }

    function metaDelegate(
        address owner,
        address delegatee,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external override {
        require(owner != address(0), "INVALID_OWNER");
        //solium-disable-next-line
        require(block.timestamp <= deadline, "INVALID_EXPIRATION");
        uint256 currentValidNonce = _nonces[owner];
        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                DOMAIN_SEPARATOR,
                keccak256(
                    abi.encode(
                        DELEGATE_TYPEHASH,
                        owner,
                        delegate,
                        currentValidNonce,
                        deadline
                    )
                )
            )
        );

        require(owner == ecrecover(digest, v, r, s), "INVALID_SIGNATURE");
    unchecked {
        // does not make sense to check because it's not realistic to reach uint256.max in nonce
        _nonces[owner] = currentValidNonce + 1;
    }
        _delegateByType(owner, delegatee, GovernancePowerType.VOTING);
        _delegateByType(owner, delegatee, GovernancePowerType.PROPOSITION);
    }

}
