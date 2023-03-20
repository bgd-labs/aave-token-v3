// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IERC20Metadata} from '../../../lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol';
import {IGovernancePowerDelegationToken} from '../../interfaces/IGovernancePowerDelegationToken.sol';

interface IAaveTokenV3 is IERC20Metadata, IGovernancePowerDelegationToken {
  /**
   * @notice Returns the current nonce for `owner`.
   */
  function _nonces(address owner) external view returns (uint256);

  /**
   * @dev Returns the domain separator used in encoding of the signature, as defined by {EIP712}.
   */
  function DOMAIN_SEPARATOR() external view returns (bytes32);

  /**
   * @dev Sets `value` as the allowance of `spender` over ``owner``'s tokens,
   * given ``owner``'s signed approval.
   *
   * IMPORTANT: The same issues {IERC20-approve} has related to transaction
   * ordering also apply here.
   *
   * Emits an {Approval} event.
   *
   * Requirements:
   *
   * - `spender` cannot be the zero address.
   * - `deadline` must be a timestamp in the future.
   * - `v`, `r` and `s` must be a valid `secp256k1` signature from `owner`
   * over the EIP712-formatted function arguments.
   * - the signature must use ``owner``'s current nonce (see {nonces}).
   *
   * For more information on the signature format, see the
   * https://eips.ethereum.org/EIPS/eip-2612#specification[relevant EIP
   * section].
   */
  function permit(
    address owner,
    address spender,
    uint256 value,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
  ) external;

  function DELEGATE_BY_TYPE_TYPEHASH() external view returns (bytes32);

  function PERMIT_TYPEHASH() external view returns (bytes32);

  function DELEGATE_TYPEHASH() external view returns (bytes32);
}
