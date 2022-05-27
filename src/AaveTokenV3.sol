// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {VersionedInitializable} from './utils/VersionedInitializable.sol';

import {IGovernancePowerDelegationToken} from './interfaces/IGovernancePowerDelegationToken.sol';
import {BaseAaveTokenV2} from './BaseAaveTokenV2.sol';

contract AaveTokenV3 is BaseAaveTokenV2, IGovernancePowerDelegationToken {
  mapping(address => address) internal _votingDelegateeV2;
  mapping(address => address) internal _propositionDelegateeV2;

  uint256 public constant DELEGATED_POWER_DIVIDER = 10**10;

  bytes32 public constant DELEGATE_BY_TYPE_TYPEHASH =
    keccak256(
      'DelegateByType(address delegator,address delegatee,GovernancePowerType delegationType,uint256 nonce,uint256 deadline)'
    );
  bytes32 public constant DELEGATE_TYPEHASH =
    keccak256('Delegate(address delegator,address delegatee,uint256 nonce,uint256 deadline)');

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
    return _getDelegateeByType(delegator, _balances[delegator], delegationType);
  }

  /// @inheritdoc IGovernancePowerDelegationToken
  function getPowerCurrent(address user, GovernancePowerType delegationType)
    external
    view
    override
    returns (uint256)
  {
    DelegationAwareBalance memory userState = _balances[user];
    uint256 userOwnPower = uint8(userState.delegationState) & (uint8(delegationType) + 1) == 0
      ? _balances[user].balance
      : 0;
    uint256 userDelegatedPower = _getDelegatedPowerByType(userState, delegationType) *
      DELEGATED_POWER_DIVIDER;
    return userOwnPower + userDelegatedPower;
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
    uint256 currentValidNonce = _nonces[delegator];
    bytes32 digest = keccak256(
      abi.encodePacked(
        '\x19\x01',
        DOMAIN_SEPARATOR,
        keccak256(
          abi.encode(
            DELEGATE_BY_TYPE_TYPEHASH,
            delegator,
            delegatee,
            delegationType,
            currentValidNonce,
            deadline
          )
        )
      )
    );

    require(delegator == ecrecover(digest, v, r, s), 'INVALID_SIGNATURE');
    unchecked {
      // does not make sense to check because it's not realistic to reach uint256.max in nonce
      _nonces[delegator] = currentValidNonce + 1;
    }
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
    uint256 currentValidNonce = _nonces[delegator];
    bytes32 digest = keccak256(
      abi.encodePacked(
        '\x19\x01',
        DOMAIN_SEPARATOR,
        keccak256(abi.encode(DELEGATE_TYPEHASH, delegator, delegatee, currentValidNonce, deadline))
      )
    );

    require(delegator == ecrecover(digest, v, r, s), 'INVALID_SIGNATURE');
    unchecked {
      // does not make sense to check because it's not realistic to reach uint256.max in nonce
      _nonces[delegator] = currentValidNonce + 1;
    }
    _delegateByType(delegator, delegatee, GovernancePowerType.VOTING);
    _delegateByType(delegator, delegatee, GovernancePowerType.PROPOSITION);
  }

  /**
   * @dev changing one of delegated governance powers of delegatee depending on the delegator balance change
   * @param delegatorBalanceBefore delegator balance before operation
   * @param delegatorBalanceAfter delegator balance after operation
   * @param delegatee the user whom delegated governance power will be changed
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   * @param operation math operation which will be applied depends on increasing or decreasing of the delegator balance (plus, minus)
   **/
  function _delegationMoveByType(
    uint104 delegatorBalanceBefore,
    uint104 delegatorBalanceAfter,
    address delegatee,
    GovernancePowerType delegationType
  ) internal {
    if (delegatee == address(0)) return;
    if (delegatorBalanceBefore == delegatorBalanceAfter) return;

    // @dev to make delegated balance fit into uin72 we're decreasing precision of delegated balance by DELEGATED_POWER_DIVIDER
    uint72 delegatorBalanceBefore72 = uint72(delegatorBalanceBefore / DELEGATED_POWER_DIVIDER);
    uint72 delegatorBalanceAfter72 = uint72(delegatorBalanceAfter / DELEGATED_POWER_DIVIDER);

    if (delegationType == GovernancePowerType.VOTING) {
      _balances[delegatee].delegatedVotingBalance =
        _balances[delegatee].delegatedVotingBalance -
        delegatorBalanceBefore72 +
        delegatorBalanceAfter72;

      //TODO: emit DelegatedPowerChanged maybe;
    } else {
      _balances[delegatee].delegatedPropositionBalance =
        _balances[delegatee].delegatedPropositionBalance -
        delegatorBalanceBefore72 +
        delegatorBalanceAfter72;
      //TODO: emit DelegatedPowerChanged maybe;
    }
  }

  /**
   * @dev changing one of governance power(Voting and Proposition) of delegatees depending on the delegator balance change
   * @param delegator delegator
   * @param delegatorState the current state of the delegator
   * @param balanceBefore delegator balance before operation
   * @param balanceAfter delegator balance after operation
   * @param operation math operation which will be applied depends on increasing or decreasing of the delegator balance (plus, minus)
   **/
  function _delegationMove(
    address delegator,
    DelegationAwareBalance memory delegatorState,
    uint104 balanceBefore,
    uint104 balanceAfter
  ) internal {
    _delegationMoveByType(
      balanceBefore,
      balanceAfter,
      _getDelegateeByType(delegator, delegatorState, GovernancePowerType.VOTING),
      GovernancePowerType.VOTING
    );
    _delegationMoveByType(
      balanceBefore,
      balanceAfter,
      _getDelegateeByType(delegator, delegatorState, GovernancePowerType.PROPOSITION),
      GovernancePowerType.PROPOSITION
    );
  }

  /**
   * @dev performs all state changes related to balance transfer and corresponding delegation changes
   * @param from token sender
   * @param to token recipient
   * @param amount amount of tokens sent
   **/
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
      require(fromUserState.balance >= amount, 'ERC20: transfer amount exceeds balance');

      uint104 fromBalanceAfter;
      unchecked {
        //TODO: in general we don't need to check cast to uint104 because we know that it's less then balance from require
        fromBalanceAfter = fromUserState.balance - uint104(amount);
      }
      _balances[from].balance = fromBalanceAfter;
      if (fromUserState.delegationState != DelegationState.NO_DELEGATION)
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

      if (toUserState.delegationState != DelegationState.NO_DELEGATION) {
        _delegationMove(to, toUserState, toUserState.balance, toBalanceBefore, MathUtils.plus);
      }
    }
  }

  /**
   * @dev extracting and returning delegated governance power(Voting or Proposition) from user state
   * @param userState the current state of a user
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   **/
  function _getDelegatedPowerByType(
    DelegationAwareBalance memory userState,
    GovernancePowerType delegationType
  ) internal pure returns (uint72) {
    return
      delegationType == GovernancePowerType.VOTING
        ? userState.delegatedVotingBalance
        : userState.delegatedPropositionBalance;
  }

  /**
   * @dev extracts from user state and returning delegatee by type of governance power(Voting or Proposition)
   * @param delegator delegator
   * @param userState the current state of a user
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   **/
  function _getDelegateeByType(
    address delegator,
    DelegationAwareBalance memory userState,
    GovernancePowerType delegationType
  ) internal view returns (address) {
    if (delegationType == GovernancePowerType.VOTING) {
      return
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
   * @dev changing user's delegatee address by type of governance power(Voting or Proposition)
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
   * @dev updates the specific flag which signaling about existence of delegation of governance power(Voting or Proposition)
   * @param userState a user state to change
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   * @param willDelegate next state of delegation
   **/
  function _updateDelegationFlagByType(
    DelegationAwareBalance memory userState,
    GovernancePowerType delegationType,
    bool willDelegate
  ) internal pure returns (DelegationAwareBalance memory) {
    if (willDelegate) {
      // because GovernancePowerType starting from 0, we should add 1 first, then we apply bitwise OR
      userState.delegationState = DelegationState(
        uint8(userState.delegationState) | (uint8(delegationType) + 1)
      );
    } else {
      // first bitwise NEGATION, ie was 01, after XOR with 11 will be 10,
      // then bitwise AND, which means it will keep only another delegation type if it exists
      userState.delegationState = DelegationState(
        uint8(userState.delegationState) & ((uint8(delegationType) + 1) ^ 3)
      );
    }
    return userState;
  }

  /**
   * @dev This is the equivalent of an ERC20 transfer(), but for a power type: an atomic transfer of a balance (power).
   * When needed, it decreases the power of the `delegator` and when needed, it increases the power of the `delegatee`
   * @param user delegator
   * @param _delegatee the user which delegated power has changed
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
    DelegationAwareBalance memory delegatorState = _balances[user];
    address currentDelegatee = _getDelegateeByType(delegator, delegatorState, delegationType);
    if (delegatee == currentDelegatee) return;

    bool delegatingNow = currentDelegatee != address(0);
    bool willDelegateAfter = delegatee != address(0);

    if (delegatingNow) {
      _delegationMoveByType(delegatorState.balance, 0, currentDelegatee, delegationType);
    }

    if (willDelegateAfter) {
      _delegationMoveByType(0, delegatorState.balance, delegatee, delegationType);
    }

    _updateDelegateeByType(delegator, delegationType, delegatee);

    if (willDelegateAfter != delegatingNow) {
      _balances[delegator] = _updateDelegationFlagByType(
        delegatorState,
        delegationType,
        willDelegateAfter
      );
    }

    emit DelegateChanged(delegator, delegatee, delegationType);
  }
}
