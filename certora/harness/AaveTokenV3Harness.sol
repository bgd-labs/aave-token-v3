// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {VersionedInitializable} from '../../src/utils/VersionedInitializable.sol';
import {IGovernancePowerDelegationToken} from '../../src/interfaces/IGovernancePowerDelegationToken.sol';
import {BaseAaveTokenV2} from '../../src/BaseAaveTokenV2.sol';

contract AaveTokenV3 is BaseAaveTokenV2, IGovernancePowerDelegationToken {


  mapping(address => address) internal _votingDelegateeV2;
  mapping(address => address) internal _propositionDelegateeV2;

  // @dev we assume that for the governance system 18 decimals of precision is not needed,
  // by this constant we reduce it by 10, to 8 decimals
  uint256 public constant DELEGATOR_POWER_SCALE_FACTOR = 1e10;

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
  function getDelegates(address delegator) external view override returns (address, address) {
    DelegationAwareBalance memory delegatorBalance = _balances[delegator];
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
    DelegationAwareBalance memory userState = _balances[user];
    uint256 userOwnPower = uint8(userState.delegationState) & (uint8(delegationType) + 1) == 0
      ? _balances[user].balance
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
      // Does not make sense to check because it's not realistic to reach uint256.max in nonce
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
   * @dev Changing one of delegated governance powers of delegatee depending on the delegator balance change
   * @param delegatorBalanceBefore delegator balance before operation
   * @param delegatorBalanceAfter delegator balance after operation
   * @param delegatee the user whom delegated governance power will be changed
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   **/
  function _governancePowerTransferByType(
    uint104 delegatorBalanceBefore,
    uint104 delegatorBalanceAfter,
    address delegatee,
    GovernancePowerType delegationType
  ) internal {
    if (delegatee == address(0)) return;
    if (delegatorBalanceBefore == delegatorBalanceAfter) return;

    // To make delegated balance fit into uint72 we're decreasing precision of delegated balance by DELEGATOR_POWER_SCALE_FACTOR
    uint72 delegatorBalanceBefore72 = uint72(delegatorBalanceBefore / DELEGATOR_POWER_SCALE_FACTOR);
    uint72 delegatorBalanceAfter72 = uint72(delegatorBalanceAfter / DELEGATOR_POWER_SCALE_FACTOR);

    if (delegationType == GovernancePowerType.VOTING) {
      _balances[delegatee].delegatedVotingBalance =
        _balances[delegatee].delegatedVotingBalance -
        delegatorBalanceBefore72 +
        delegatorBalanceAfter72;
    } else {
      _balances[delegatee].delegatedPropositionBalance =
        _balances[delegatee].delegatedPropositionBalance -
        delegatorBalanceBefore72 +
        delegatorBalanceAfter72;
    }
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
        fromBalanceAfter = fromUserState.balance - uint104(amount);
      }
      _balances[from].balance = fromBalanceAfter;
      if (fromUserState.delegationState != DelegationState.NO_DELEGATION) {
        _governancePowerTransferByType(
          fromUserState.balance,
          fromBalanceAfter,
          _getDelegateeByType(from, fromUserState, GovernancePowerType.VOTING),
          GovernancePowerType.VOTING
        );
        _governancePowerTransferByType(
          fromUserState.balance,
          fromBalanceAfter,
          _getDelegateeByType(from, fromUserState, GovernancePowerType.PROPOSITION),
          GovernancePowerType.PROPOSITION
        );
      }
    }

    if (to != address(0)) {
      DelegationAwareBalance memory toUserState = _balances[to];
      uint104 toBalanceBefore = toUserState.balance;
      toUserState.balance = toBalanceBefore + uint104(amount); // TODO: check overflow?
      _balances[to] = toUserState;

      if (toUserState.delegatingVoting || toUserState.delegatingProposition) {
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
   * @param user delegator
   * @param userState the current state of a user
   * @param delegationType the type of governance power delegation (VOTING, PROPOSITION)
   **/
  function _getDelegateeByType(
    address user,
    DelegationAwareBalance memory userState,
    GovernancePowerType delegationType
  ) internal view returns (address) {
    if (delegationType == GovernancePowerType.VOTING) {
      return userState.delegatingVoting ? _votingDelegateeV2[user] : address(0);
    }
    return userState.delegatingProposition ? _propositionDelegateeV2[user] : address(0);
  }

  /**
   * @dev changing user's delegatee address by type of governance power(Voting or Proposition)
   * @param user delegator
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
    DelegationAwareBalance memory userState,
    GovernancePowerType delegationType,
    bool willDelegate
  ) internal pure returns (DelegationAwareBalance memory) {
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
    DelegationAwareBalance memory delegatorState = _balances[delegator];
    address currentDelegatee = _getDelegateeByType(delegator, delegatorState, delegationType);
    if (delegatee == currentDelegatee) return;

    bool delegatingNow = currentDelegatee != address(0);
    bool willDelegateAfter = delegatee != address(0);

    if (delegatingNow) {
      _governancePowerTransferByType(delegatorState.balance, 0, currentDelegatee, delegationType);
    }

    if (willDelegateAfter) {
      _governancePowerTransferByType(0, delegatorState.balance, delegatee, delegationType);
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

   /** 
    Harness section - replace struct reads and writes with function calls
   */

//   struct DelegationAwareBalance {
//     uint104 balance;
//     uint72 delegatedPropositionBalance;
//     uint72 delegatedVotingBalance;
//     bool delegatingProposition;
//     bool delegatingVoting;
//   }


   function getBalance(address user) view public returns (uint104) {
    return _balances[user].balance;
   }

   function getDelegatedPropositionBalance(address user) view public returns (uint72) {
    return _balances[user].delegatedPropositionBalance;
   }


   function getDelegatedVotingBalance(address user) view public returns (uint72) {
    return _balances[user].delegatedVotingBalance;
   }


   function getDelegatingProposition(address user) view public returns (bool) {
    return _balances[user].delegationState == DelegationState.PROPOSITION_DELEGATED ||
        _balances[user].delegationState == DelegationState.FULL_POWER_DELEGATED;
   }


   function getDelegatingVoting(address user) view public returns (bool) {
     return _balances[user].delegationState == DelegationState.VOTING_DELEGATED ||
        _balances[user].delegationState == DelegationState.FULL_POWER_DELEGATED;
   }

   function getVotingDelegate(address user) view public returns (address) {
    return _votingDelegateeV2[user];
   }

   function getPropositionDelegate(address user) view public returns (address) {
    return _propositionDelegateeV2[user];
   }



   /**
     End of harness section
    */
}
