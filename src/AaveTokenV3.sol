// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {VersionedInitializable} from "./utils/VersionedInitializable.sol";

import {IGovernancePowerDelegationToken} from "./interfaces/IGovernancePowerDelegationToken.sol";
import {BaseAaveToken} from "./BaseAaveToken.sol";

contract AaveTokenV3 is
    BaseAaveToken,
    VersionedInitializable,
    IGovernancePowerDelegationToken
{
    /// @dev owner => next valid nonce to submit with permit()
    mapping(address => uint256) public _nonces;

    ///////// @dev DEPRECATED from AaveToken v1  //////////////////////////
    //////// kept for backwards compatibility with old storage layout ////
    uint256[3] private ______DEPRECATED_FROM_AAVE_V1;
    ///////// @dev END OF DEPRECATED from AaveToken v1  //////////////////////////

    bytes32 public DOMAIN_SEPARATOR;

    ///////// @dev DEPRECATED from AaveToken v2  //////////////////////////
    //////// kept for backwards compatibility with old storage layout ////
    uint256[4] private ______DEPRECATED_FROM_AAVE_V2;
    ///////// @dev END OF DEPRECATED from AaveToken v2  //////////////////////////

    bytes public constant EIP712_REVISION = bytes("1");
    bytes32 internal constant EIP712_DOMAIN =
        keccak256(
            "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
        );
    bytes32 public constant PERMIT_TYPEHASH =
        keccak256(
            "Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"
        );

    uint256 public constant REVISION = 3; // TODO: CHECK, but most probably was 2 before

    mapping(address => address) private _votingDelegateeV2;
    mapping(address => address) private _propositionDelegateeV2;

    uint256 public constant DELEGATED_POWER_DIVIDER = 10**10;

    /**
     * @dev initializes the contract upon assignment to the InitializableAdminUpgradeabilityProxy
     */
    function initialize() external initializer {}

    function _plus(uint72 a, uint72 b) internal pure returns (uint72) {
        return a + b;
    }

    function _minus(uint72 a, uint72 b) internal pure returns (uint72) {
        return a - b;
    }

    function _delegationMove(
        uint104 userBalanceBefore,
        uint104 userBalanceAfter,
        address votingDelegatee,
        address propositionDelegatee,
        function(uint72, uint72) returns (uint72) operation
    ) internal {
        uint72 delegationDelta = uint72(
            (userBalanceBefore / DELEGATED_POWER_DIVIDER) -
                (userBalanceAfter / DELEGATED_POWER_DIVIDER)
        );
        if (votingDelegatee != address(0)) {
            _balances[votingDelegatee].delegatedVotingBalance = operation(
                _balances[votingDelegatee].delegatedVotingBalance,
                delegationDelta
            );
        }
        if (propositionDelegatee != address(0)) {
            _balances[propositionDelegatee]
                .delegatedPropositionBalance = operation(
                _balances[propositionDelegatee].delegatedPropositionBalance,
                delegationDelta
            );
        }
    }

    function _delegationMoveOverOptimal(
        uint104 userBalanceBefore,
        uint104 userBalanceAfter,
        address votingDelegatee,
        address propositionDelegatee,
        function(uint72, uint72) returns (uint72) operation
    ) internal {
        address delegate1Address = votingDelegatee != address(0)
            ? votingDelegatee
            : propositionDelegatee;
        if (delegate1Address == address(0)) {
            return;
        }

        uint72 delegationDelta = uint72(
            (userBalanceBefore / DELEGATED_POWER_DIVIDER) -
                (userBalanceAfter / DELEGATED_POWER_DIVIDER)
        );
        DelegationAwareBalance memory delegate1State = _balances[
            delegate1Address
        ];
        if (votingDelegatee == propositionDelegatee) {
            delegate1State.delegatedVotingBalance = operation(
                delegate1State.delegatedVotingBalance,
                delegationDelta
            );
            delegate1State.delegatedPropositionBalance = operation(
                delegate1State.delegatedPropositionBalance,
                delegationDelta
            );
        } else if (votingDelegatee != address(0)) {
            delegate1State.delegatedVotingBalance = operation(
                delegate1State.delegatedVotingBalance,
                delegationDelta
            );
            if (propositionDelegatee != address(0)) {
                _balances[propositionDelegatee]
                    .delegatedPropositionBalance = operation(
                    _balances[propositionDelegatee].delegatedPropositionBalance,
                    delegationDelta
                );
            }
        } else {
            delegate1State.delegatedPropositionBalance = operation(
                delegate1State.delegatedPropositionBalance,
                delegationDelta
            );
        }
        _balances[delegate1Address] = delegate1State;
        //TODO: emit DelegatedPowerChanged;
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
                fromUserState.delegatingVoting ||
                fromUserState.delegatingProposition
            ) {
                (
                    address votingDelegatee,
                    address propositionDelegatee
                ) = _getDelegaties(from, fromUserState);
                _delegationMove(
                    fromUserState.balance,
                    fromBalanceAfter,
                    votingDelegatee,
                    propositionDelegatee,
                    _minus
                );
            }
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
                (
                    address votingDelegatee,
                    address propositionDelegatee
                ) = _getDelegaties(to, toUserState);
                _delegationMove(
                    toUserState.balance,
                    toBalanceBefore,
                    votingDelegatee,
                    propositionDelegatee,
                    _plus
                );
            }
        }
    }

    function _getDelegaties(
        address user,
        DelegationAwareBalance memory userState
    ) internal view returns (address, address) {
        return (
            userState.delegatingVoting ? _votingDelegateeV2[user] : address(0),
            userState.delegatingProposition
                ? _propositionDelegateeV2[user]
                : address(0)
        );
    }

    function delegateByType(
        address delegatee,
        GovernancePowerType delegationType
    ) external virtual override {
        DelegationAwareBalance memory userState = _balances[msg.sender];
        (
            address votingPowerDelegatee,
            address propositionPowerDelegatee
        ) = _getDelegaties(msg.sender, userState);

        //if user will delegate to self - then cleanup
        bool willDelegateAfter = delegatee != msg.sender &&
            delegatee != address(0);

        if (delegationType == GovernancePowerType.VOTING) {
            if (userState.delegatingVoting) {
                if (delegatee == votingPowerDelegatee) return;
                _delegationMove(
                    userState.balance,
                    0,
                    votingPowerDelegatee,
                    address(0),
                    _minus
                );
            }
            if (willDelegateAfter) {
                _votingDelegateeV2[msg.sender] = delegatee;
                _delegationMove(
                    userState.balance,
                    0,
                    delegatee,
                    address(0),
                    _plus
                );
            }
            if (willDelegateAfter != userState.delegatingVoting) {
                userState.delegatingVoting = willDelegateAfter;
                _balances[msg.sender] = userState;
            }
            if (votingPowerDelegatee != delegatee) {
                emit DelegateChanged(
                    votingPowerDelegatee,
                    delegatee,
                    GovernancePowerType.VOTING
                );
            }
        } else {
            if (userState.delegatingProposition) {
                if (delegatee == propositionPowerDelegatee) return;
                _delegationMove(
                    userState.balance,
                    0,
                    address(0),
                    propositionPowerDelegatee,
                    _minus
                );
            }
            if (willDelegateAfter) {
                _propositionDelegateeV2[msg.sender] = delegatee;
                _delegationMove(
                    userState.balance,
                    0,
                    address(0),
                    delegatee,
                    _plus
                );
            }

            if (willDelegateAfter != userState.delegatingProposition) {
                userState.delegatingProposition = willDelegateAfter;
                _balances[msg.sender] = userState;
            }
            if (propositionPowerDelegatee != delegatee) {
                emit DelegateChanged(
                    propositionPowerDelegatee,
                    delegatee,
                    GovernancePowerType.PROPOSITION
                );
            }
        }
    }

    /**
     * @dev delegates all the powers to a specific user
     * @param delegatee the user to which the power will be delegated
     **/
    function delegate(address delegatee) external override {
        DelegationAwareBalance memory userState = _balances[msg.sender];
        (
            address currentVotingPowerDelegatee,
            address currentPropositionPowerDelegatee
        ) = _getDelegaties(msg.sender, userState);

        //if user will delegate to self - then cleanup
        bool willDelegateAfter = delegatee != msg.sender &&
            delegatee != address(0);

        _delegationMove(
            userState.balance,
            0,
            currentVotingPowerDelegatee != delegatee
                ? currentVotingPowerDelegatee
                : address(0),
            currentPropositionPowerDelegatee != delegatee
                ? currentPropositionPowerDelegatee
                : address(0),
            _minus
        );

        if (willDelegateAfter) {
            _votingDelegateeV2[msg.sender] = delegatee;
            _propositionDelegateeV2[msg.sender] = delegatee;
            _delegationMove(
                userState.balance,
                0,
                currentVotingPowerDelegatee != delegatee
                    ? delegatee
                    : address(0),
                currentPropositionPowerDelegatee != delegatee
                    ? delegatee
                    : address(0),
                _plus
            );
        }
        if (
            willDelegateAfter != userState.delegatingVoting ||
            willDelegateAfter != userState.delegatingProposition
        ) {
            userState.delegatingVoting = willDelegateAfter;
            userState.delegatingProposition = willDelegateAfter;
            _balances[msg.sender] = userState;
        }

        if (currentVotingPowerDelegatee != delegatee) {
            emit DelegateChanged(
                currentVotingPowerDelegatee,
                delegatee,
                GovernancePowerType.VOTING
            );
        }
        if (currentPropositionPowerDelegatee != delegatee) {
            emit DelegateChanged(
                currentPropositionPowerDelegatee,
                delegatee,
                GovernancePowerType.PROPOSITION
            );
        }
    }

    function getDelegateeByType(
        address delegator,
        GovernancePowerType delegationType
    ) external view override returns (address) {
        return
            delegationType == GovernancePowerType.VOTING
                ? _votingDelegateeV2[delegator]
                : _propositionDelegateeV2[delegator];
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
        uint256 userDelegatedPower = delegationType ==
            GovernancePowerType.VOTING
            ? _balances[user].delegatedVotingBalance
            : _balances[user].delegatedPropositionBalance;
        return userOwnPower + userDelegatedPower * DELEGATED_POWER_DIVIDER;
    }

    /**
     * @dev implements the permit function as for https://github.com/ethereum/EIPs/blob/8a34d644aacf0f9f8f00815307fd7dd5da07655f/EIPS/eip-2612.md
     * @param owner the owner of the funds
     * @param spender the spender
     * @param value the amount
     * @param deadline the deadline timestamp, type(uint256).max for no deadline
     * @param v signature param
     * @param s signature param
     * @param r signature param
     */

    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external {
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
                        PERMIT_TYPEHASH,
                        owner,
                        spender,
                        value,
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
        _approve(owner, spender, value);
    }

    /**
     * @dev returns the revision of the implementation contract
     */
    function getRevision() internal pure override returns (uint256) {
        return REVISION;
    }
}
