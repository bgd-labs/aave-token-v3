// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IGovernancePowerDelegationToken} from './interfaces/IGovernancePowerDelegationToken.sol';
import {DelegationState} from './DelegationAwareBalance.sol';

abstract contract BaseDelegation is IGovernancePowerDelegationToken {
  struct DelegationBalance {
    uint72 delegatedPropositionBalance;
    uint72 delegatedVotingBalance;
    DelegationState delegationState;
  }

  mapping(address => address) internal _votingDelegateeV2;
  mapping(address => address) internal _propositionDelegateeV2;

  /// @dev we assume that for the governance system 18 decimals of precision is not needed,
  // by this constant we reduce it by 10, to 8 decimals
  uint256 public constant POWER_SCALE_FACTOR = 1e10;

  bytes32 public constant DELEGATE_BY_TYPE_TYPEHASH =
    keccak256(
      'DelegateByType(address delegator,address delegatee,uint8 delegationType,uint256 nonce,uint256 deadline)'
    );
  bytes32 public constant DELEGATE_TYPEHASH =
    keccak256('Delegate(address delegator,address delegatee,uint256 nonce,uint256 deadline)');

  function _getDomainSeparator() internal view virtual returns (bytes32);

  function _getDelegationBalance(address user)
    internal
    view
    virtual
    returns (DelegationBalance memory);

  function _getBalance(address user) internal view virtual returns (uint256);

  function _incrementNonces(address user) internal virtual returns (uint256);

  function _setDelegationBalance(address user, DelegationBalance memory balance) internal virtual;

  /// @inheritdoc IGovernancePowerDelegationToken
  function delegateByType(address delegatee, GovernancePowerType delegationType)
    external
    virtual
    override
  {
    _delegateByType(msg.sender, delegatee, delegationType);
  }

  /// @inheritdoc IGovernancePowerDelegationToken
  function delegate(address delegatee) external override {
    _delegateByType(msg.sender, delegatee, GovernancePowerType.VOTING);
    _delegateByType(msg.sender, delegatee, GovernancePowerType.PROPOSITION);
  }

  /// @inheritdoc IGovernancePowerDelegationToken
  function getDelegateeByType(address delegator, GovernancePowerType delegationType)
    external
    view
    override
    returns (address)
  {
    return _getDelegateeByType(delegator, _getDelegationBalance(delegator), delegationType);
  }

  /// @inheritdoc IGovernancePowerDelegationToken
  function getDelegates(address delegator) external view override returns (address, address) {
    DelegationBalance memory delegatorBalance = _getDelegationBalance(delegator);
    return (
      _getDelegateeByType(delegator, delegatorBalance, GovernancePowerType.VOTING),
      _getDelegateeByType(delegator, delegatorBalance, GovernancePowerType.PROPOSITION)
    );
  }

  /// @inheritdoc IGovernancePowerDelegationToken
  function getPowerCurrent(address user, GovernancePowerType delegationType)
    public
    view
    override
    returns (uint256)
  {
    DelegationBalance memory userState = _getDelegationBalance(user);
    uint256 userOwnPower = uint8(userState.delegationState) & (uint8(delegationType) + 1) == 0
      ? _getBalance(user)
      : 0;
    uint256 userDelegatedPower = _getDelegatedPowerByType(userState, delegationType);
    return userOwnPower + userDelegatedPower;
  }

  /// @inheritdoc IGovernancePowerDelegationToken
  function getPowersCurrent(address user) external view override returns (uint256, uint256) {
    return (
      getPowerCurrent(user, GovernancePowerType.VOTING),
      getPowerCurrent(user, GovernancePowerType.PROPOSITION)
    );
  }

  /// @inheritdoc IGovernancePowerDelegationToken
  function metaDelegateByType(
    address delegator,
    address delegatee,
    GovernancePowerType delegationType,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
  ) external override {
    require(delegator != address(0), 'INVALID_OWNER');
    //solium-disable-next-line
    require(block.timestamp <= deadline, 'INVALID_EXPIRATION');
    bytes32 digest = keccak256(
      abi.encodePacked(
        '\x19\x01',
        _getDomainSeparator(),
        keccak256(
          abi.encode(
            DELEGATE_BY_TYPE_TYPEHASH,
            delegator,
            delegatee,
            delegationType,
            _incrementNonces(delegator),
            deadline
          )
        )
      )
    );

    require(delegator == ecrecover(digest, v, r, s), 'INVALID_SIGNATURE');
    _delegateByType(delegator, delegatee, delegationType);
  }

  /// @inheritdoc IGovernancePowerDelegationToken
  function metaDelegate(
    address delegator,
    address delegatee,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
  ) external override {
    require(delegator != address(0), 'INVALID_OWNER');
    //solium-disable-next-line
    require(block.timestamp <= deadline, 'INVALID_EXPIRATION');
    bytes32 digest = keccak256(
      abi.encodePacked(
        '\x19\x01',
        _getDomainSeparator(),
        keccak256(
          abi.encode(DELEGATE_TYPEHASH, delegator, delegatee, _incrementNonces(delegator), deadline)
        )
      )
    );

    require(delegator == ecrecover(digest, v, r, s), 'INVALID_SIGNATURE');
    _delegateByType(delegator, delegatee, GovernancePowerType.VOTING);
    _delegateByType(delegator, delegatee, GovernancePowerType.PROPOSITION);
  }

  /**
   * @dev Modifies the delegated power of a `delegatee` account by type (VOTING, PROPOSITION).
   * Passing the impact on the delegation of `delegatee` account before and after to reduce conditionals and not lose
   * any precision.
   * @param impactOnDelegationBefore how much impact a balance of another account had over the delegation of a `delegatee`
   * before an action.
   * For example, if the action is a delegation from one account to another, the impact before the action will be 0.
   * @param impactOnDelegationAfter how much impact a balance of another account will have  over the delegation of a `delegatee`
   * after an action.
   * For example, if the action is a delegation from one account to another, the impact after the action will be the whole balance
   * of the account changing the delegatee.
   * @param delegatee the user whom delegated governance power will be changed
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   **/
  function _governancePowerTransferByType(
    uint256 impactOnDelegationBefore,
    uint256 impactOnDelegationAfter,
    address delegatee,
    GovernancePowerType delegationType
  ) internal {
    if (delegatee == address(0)) return;
    if (impactOnDelegationBefore == impactOnDelegationAfter) return;

    // we use uint72, because this is the most optimal for AaveTokenV3
    // To make delegated balance fit into uint72 we're decreasing precision of delegated balance by POWER_SCALE_FACTOR
    // TODO: safe-cast?
    uint72 impactOnDelegationBefore72 = uint72(impactOnDelegationBefore / POWER_SCALE_FACTOR);
    uint72 impactOnDelegationAfter72 = uint72(impactOnDelegationAfter / POWER_SCALE_FACTOR);

    DelegationBalance memory delegateeState = _getDelegationBalance(delegatee);
    if (delegationType == GovernancePowerType.VOTING) {
      delegateeState.delegatedVotingBalance =
        delegateeState.delegatedVotingBalance -
        impactOnDelegationBefore72 +
        impactOnDelegationAfter72;
    } else {
      delegateeState.delegatedPropositionBalance =
        delegateeState.delegatedPropositionBalance -
        impactOnDelegationBefore72 +
        impactOnDelegationAfter72;
    }
    _setDelegationBalance(delegatee, delegateeState);
  }

  /**
   * @dev performs all state changes related delegation changes on transfer
   * @param from token sender
   * @param to token recipient
   * @param fromBalanceBefore balance of the sender before transfer
   * @param toBalanceBefore balance of the recipient before transfer
   * @param amount amount of tokens sent
   **/
  function _delegationChangeOnTransfer(
    address from,
    address to,
    uint256 fromBalanceBefore,
    uint256 toBalanceBefore,
    uint256 amount
  ) internal {
    if (from == to) {
      return;
    }

    if (from != address(0)) {
      DelegationBalance memory fromUserState = _getDelegationBalance(from);
      uint256 fromBalanceAfter = fromBalanceBefore - amount;
      if (fromUserState.delegationState != DelegationState.NO_DELEGATION) {
        _governancePowerTransferByType(
          fromBalanceBefore,
          fromBalanceAfter,
          _getDelegateeByType(from, fromUserState, GovernancePowerType.VOTING),
          GovernancePowerType.VOTING
        );
        _governancePowerTransferByType(
          fromBalanceBefore,
          fromBalanceAfter,
          _getDelegateeByType(from, fromUserState, GovernancePowerType.PROPOSITION),
          GovernancePowerType.PROPOSITION
        );
      }
    }

    if (to != address(0)) {
      DelegationBalance memory toUserState = _getDelegationBalance(to);
      uint256 toBalanceAfter = toBalanceBefore + amount;

      if (toUserState.delegationState != DelegationState.NO_DELEGATION) {
        _governancePowerTransferByType(
          toBalanceBefore,
          toBalanceAfter,
          _getDelegateeByType(to, toUserState, GovernancePowerType.VOTING),
          GovernancePowerType.VOTING
        );
        _governancePowerTransferByType(
          toBalanceBefore,
          toBalanceAfter,
          _getDelegateeByType(to, toUserState, GovernancePowerType.PROPOSITION),
          GovernancePowerType.PROPOSITION
        );
      }
    }
  }

  /**
   * @dev Extracts from state and returns delegated governance power (Voting, Proposition)
   * @param userState the current state of a user
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   **/
  function _getDelegatedPowerByType(
    DelegationBalance memory userState,
    GovernancePowerType delegationType
  ) internal pure returns (uint256) {
    return
      POWER_SCALE_FACTOR *
      (
        delegationType == GovernancePowerType.VOTING
          ? userState.delegatedVotingBalance
          : userState.delegatedPropositionBalance
      );
  }

  /**
   * @dev Extracts from state and returns the delegatee of a delegator by type of governance power (Voting, Proposition)
   * - If the delegator doesn't have any delegatee, returns address(0)
   * @param delegator delegator
   * @param userState the current state of a user
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   **/
  function _getDelegateeByType(
    address delegator,
    DelegationBalance memory userState,
    GovernancePowerType delegationType
  ) internal view returns (address) {
    if (delegationType == GovernancePowerType.VOTING) {
      return
        /// With the & operation, we cover both VOTING_DELEGATED delegation and FULL_POWER_DELEGATED
        /// as VOTING_DELEGATED is equivalent to 01 in binary and FULL_POWER_DELEGATED is equivalent to 11
        (uint8(userState.delegationState) & uint8(DelegationState.VOTING_DELEGATED)) != 0
          ? _votingDelegateeV2[delegator]
          : address(0);
    }
    return
      userState.delegationState >= DelegationState.PROPOSITION_DELEGATED
        ? _propositionDelegateeV2[delegator]
        : address(0);
  }

  /**
   * @dev Changes user's delegatee address by type of governance power (Voting, Proposition)
   * @param delegator delegator
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   * @param _newDelegatee the new delegatee
   **/
  function _updateDelegateeByType(
    address delegator,
    GovernancePowerType delegationType,
    address _newDelegatee
  ) internal {
    address newDelegatee = _newDelegatee == delegator ? address(0) : _newDelegatee;
    if (delegationType == GovernancePowerType.VOTING) {
      _votingDelegateeV2[delegator] = newDelegatee;
    } else {
      _propositionDelegateeV2[delegator] = newDelegatee;
    }
  }

  /**
   * @dev Updates the specific flag which signaling about existence of delegation of governance power (Voting, Proposition)
   * @param userState a user state to change
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   * @param willDelegate next state of delegation
   **/
  function _updateDelegationFlagByType(
    DelegationBalance memory userState,
    GovernancePowerType delegationType,
    bool willDelegate
  ) internal pure returns (DelegationBalance memory) {
    if (willDelegate) {
      // Because GovernancePowerType starts from 0, we should add 1 first, then we apply bitwise OR
      userState.delegationState = DelegationState(
        uint8(userState.delegationState) | (uint8(delegationType) + 1)
      );
    } else {
      // First bitwise NEGATION, ie was 01, after XOR with 11 will be 10,
      // then bitwise AND, which means it will keep only another delegation type if it exists
      userState.delegationState = DelegationState(
        uint8(userState.delegationState) &
          ((uint8(delegationType) + 1) ^ uint8(DelegationState.FULL_POWER_DELEGATED))
      );
    }
    return userState;
  }

  /**
   * @dev This is the equivalent of an ERC20 transfer(), but for a power type: an atomic transfer of a balance (power).
   * When needed, it decreases the power of the `delegator` and when needed, it increases the power of the `delegatee`
   * @param delegator delegator
   * @param _delegatee the user which delegated power will change
   * @param delegationType the type of delegation (VOTING, PROPOSITION)
   **/
  function _delegateByType(
    address delegator,
    address _delegatee,
    GovernancePowerType delegationType
  ) internal {
    // Here we unify the property that delegating power to address(0) == delegating power to yourself == no delegation
    // So from now on, not being delegating is (exclusively) that delegatee == address(0)
    address delegatee = _delegatee == delegator ? address(0) : _delegatee;

    // We read the whole struct before validating delegatee, because in the optimistic case
    // (_delegatee != currentDelegatee) we will reuse userState in the rest of the function
    DelegationBalance memory delegatorState = _getDelegationBalance(delegator);
    address currentDelegatee = _getDelegateeByType(delegator, delegatorState, delegationType);
    if (delegatee == currentDelegatee) return;

    bool delegatingNow = currentDelegatee != address(0);
    bool willDelegateAfter = delegatee != address(0);
    uint256 delegatorBalance = _getBalance(delegator);

    if (delegatingNow) {
      _governancePowerTransferByType(delegatorBalance, 0, currentDelegatee, delegationType);
    }

    if (willDelegateAfter) {
      _governancePowerTransferByType(0, delegatorBalance, delegatee, delegationType);
    }

    _updateDelegateeByType(delegator, delegationType, delegatee);

    if (willDelegateAfter != delegatingNow) {
      _setDelegationBalance(
        delegator,
        _updateDelegationFlagByType(delegatorState, delegationType, willDelegateAfter)
      );
    }

    emit DelegateChanged(delegator, delegatee, delegationType);
  }
}
