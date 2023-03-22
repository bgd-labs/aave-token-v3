// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IERC20Metadata} from 'openzeppelin-contracts/token/ERC20/extensions/IERC20Metadata.sol';
import {IERC20Permit} from 'openzeppelin-contracts/token/ERC20/extensions/draft-IERC20Permit.sol';
import {IGovernancePowerDelegationToken} from '../interfaces/IGovernancePowerDelegationToken.sol';

interface IAaveTokenV3 is IERC20Metadata, IERC20Permit, IGovernancePowerDelegationToken {
  /**
   * @notice Returns the current nonce for `owner`.
   * @dev Backward compatible version of nonces
   */
  function _nonces(address owner) external view returns (uint256);

  function DELEGATE_BY_TYPE_TYPEHASH() external view returns (bytes32);

  function PERMIT_TYPEHASH() external view returns (bytes32);

  function DELEGATE_TYPEHASH() external view returns (bytes32);
}
