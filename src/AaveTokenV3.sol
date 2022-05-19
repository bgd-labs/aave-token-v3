// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {VersionedInitializable} from "./utils/VersionedInitializable.sol";

import {IGovernancePowerDelegationToken} from "./interfaces/IGovernancePowerDelegationToken.sol";
import {BaseAaveTokenV2} from "./BaseAaveTokenV2.sol";

contract AaveTokenV3 is BaseAaveTokenV2, IGovernancePowerDelegationToken {
    mapping(address => address) private _votingDelegateeV2;
    mapping(address => address) private _propositionDelegateeV2;

    uint256 public constant DELEGATED_POWER_DIVIDER = 10**10;

    function _plus(uint72 a, uint72 b) internal pure returns (uint72) {
        return a + b;
    }

    function _minus(uint72 a, uint72 b) internal pure returns (uint72) {
        return a - b;
    }

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
                    _minus
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
                    _plus
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
                _minus
            );
        }
        if (willDelegateAfter) {
            _updateDelegateeByType(user, delegationType, delegatee);
            _delegationMoveByType(
                userState.balance,
                0,
                delegatee,
                delegationType,
                _plus
            );
        }

        if (willDelegateAfter != delegatingNow) {
            _balances[user] = _updateDelegationFlagByType(
                userState,
                delegationType,
                willDelegateAfter
            );
        }

        if (currentDelegatee != delegatee) {
            emit DelegateChanged(user, delegatee, delegationType);
        }
    }

    function delegateByType(
        address _delegatee,
        GovernancePowerType delegationType
    ) external virtual override {
        _delegateByType(msg.sender, _delegatee, delegationType);
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
}
