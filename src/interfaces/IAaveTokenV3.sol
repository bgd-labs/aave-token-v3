// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IERC20Metadata} from 'openzeppelin-contracts/token/ERC20/extensions/IERC20Metadata.sol';
import {IERC20Permit} from 'openzeppelin-contracts/token/ERC20/extensions/IERC20Permit.sol';
import {IGovernancePowerDelegationToken} from '../interfaces/IGovernancePowerDelegationToken.sol';

interface IAaveTokenV3 is IERC20Metadata, IERC20Permit, IGovernancePowerDelegationToken {

  /**
   * @notice The permit typehash used in the permit signature
   * @return The typehash for the permit
   */
  function PERMIT_TYPEHASH() external view returns (bytes32);
}
