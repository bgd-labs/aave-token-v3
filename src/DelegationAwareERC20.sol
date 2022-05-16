// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v4.5.0) (token/ERC20/ERC20.sol)

pragma solidity ^0.8.0;

import {IERC20} from "../lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import {IERC20Metadata} from "../lib/openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import {Context} from "../lib/openzeppelin-contracts/contracts/utils/Context.sol";
import {VersionedInitializable} from "./utils/VersionedInitializable.sol";

import {IGovernancePowerDelegationToken} from "./interfaces/IGovernancePowerDelegationToken.sol";
import {BaseERC20Storage} from "./BaseERC20Storage.sol";

/**
 * @dev Implementation of the {IERC20} interface.
 *
 * This implementation is agnostic to the way tokens are created. This means
 * that a supply mechanism has to be added in a derived contract using {_mint}.
 * For a generic mechanism see {ERC20PresetMinterPauser}.
 *
 * TIP: For a detailed writeup see our guide
 * https://forum.zeppelin.solutions/t/how-to-implement-erc20-supply-mechanisms/226[How
 * to implement supply mechanisms].
 *
 * We have followed general OpenZeppelin Contracts guidelines: functions revert
 * instead returning `false` on failure. This behavior is nonetheless
 * conventional and does not conflict with the expectations of ERC20
 * applications.
 *
 * Additionally, an {Approval} event is emitted on calls to {transferFrom}.
 * This allows applications to reconstruct the allowance for all accounts just
 * by listening to said events. Other implementations of the EIP may not emit
 * these events, as it isn't required by the specification.
 *
 * Finally, the non-standard {decreaseAllowance} and {increaseAllowance}
 * functions have been added to mitigate the well-known issues around setting
 * allowances. See {IERC20-approve}.
 */
contract DelegationAwareERC20 is
    Context,
    BaseERC20Storage,
    VersionedInitializable,
    IERC20,
    IERC20Metadata,
    IGovernancePowerDelegationToken
{
    /// @dev owner => next valid nonce to submit with permit()
    mapping(address => uint256) public _nonces;

    ///////// @dev DEPRECATED from AaveToken v1  //////////////////////////
    //////// kept for backwards compatibility with old storage layout ////
    mapping(address => mapping(uint256 => uint256)) public _snapshots;
    mapping(address => uint256) public _countsSnapshots;
    address private _aaveGovernance;
    ///////// @dev END OF DEPRECATED from AaveToken v1  //////////////////////////

    bytes32 public DOMAIN_SEPARATOR;

    ///////// @dev DEPRECATED from AaveToken v2  //////////////////////////
    //////// kept for backwards compatibility with old storage layout ////
    mapping(address => address) internal _votingDelegates;
    mapping(address => mapping(uint256 => uint256))
        internal _propositionPowerSnapshots;
    mapping(address => uint256) internal _propositionPowerSnapshotsCounts;

    mapping(address => address) internal _propositionPowerDelegates;
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

    uint256 public constant REVISION = 3; // TODO: CHECK, but most probably was 1 before

    mapping(address => address) private _votingDelegateV2;
    mapping(address => address) private _propositionDelegateV2;

    uint256 public constant DELEGATED_POWER_DIVIDER = 10**10;

    /**
     * @dev Sets the values for {name} and {symbol}.
     *
     * The default value of {decimals} is 18. To select a different value for
     * {decimals} you should overload it.
     *
     * All two of these values are immutable: they can only be set once during
     * construction.
     */
    constructor(string memory name_, string memory symbol_) {
        _name = name_;
        _symbol = symbol_;
    }

    /**
     * @dev initializes the contract upon assignment to the InitializableAdminUpgradeabilityProxy
     */
    function initialize() external initializer {
        uint256 chainId;

        //solium-disable-next-line
        assembly {
            chainId := chainid()
        }

        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                EIP712_DOMAIN,
                keccak256(bytes(_name)), //TODO: using it, knowing that variable already initialized
                keccak256(EIP712_REVISION),
                chainId,
                address(this)
            )
        );
    }

    /**
     * @dev Returns the name of the token.
     */
    function name() public view virtual override returns (string memory) {
        return _name;
    }

    /**
     * @dev Returns the symbol of the token, usually a shorter version of the
     * name.
     */
    function symbol() public view virtual override returns (string memory) {
        return _symbol;
    }

    /**
     * @dev Returns the number of decimals used to get its user representation.
     * For example, if `decimals` equals `2`, a balance of `505` tokens should
     * be displayed to a user as `5.05` (`505 / 10 ** 2`).
     *
     * Tokens usually opt for a value of 18, imitating the relationship between
     * Ether and Wei. This is the value {ERC20} uses, unless this function is
     * overridden;
     *
     * NOTE: This information is only used for _display_ purposes: it in
     * no way affects any of the arithmetic of the contract, including
     * {IERC20-balanceOf} and {IERC20-transfer}.
     */
    function decimals() public view virtual override returns (uint8) {
        return 18;
    }

    /**
     * @dev See {IERC20-totalSupply}.
     */
    function totalSupply() public view virtual override returns (uint256) {
        return _totalSupply;
    }

    /**
     * @dev See {IERC20-balanceOf}.
     */
    function balanceOf(address account)
        public
        view
        virtual
        override
        returns (uint256)
    {
        return _balances[account].balance;
    }

    /**
     * @dev See {IERC20-transfer}.
     *
     * Requirements:
     *
     * - `to` cannot be the zero address.
     * - the caller must have a balance of at least `amount`.
     */
    function transfer(address to, uint256 amount)
        public
        virtual
        override
        returns (bool)
    {
        address owner = _msgSender();
        _transfer(owner, to, amount);
        return true;
    }

    /**
     * @dev See {IERC20-allowance}.
     */
    function allowance(address owner, address spender)
        public
        view
        virtual
        override
        returns (uint256)
    {
        return _allowances[owner][spender];
    }

    /**
     * @dev See {IERC20-approve}.
     *
     * NOTE: If `amount` is the maximum `uint256`, the allowance is not updated on
     * `transferFrom`. This is semantically equivalent to an infinite approval.
     *
     * Requirements:
     *
     * - `spender` cannot be the zero address.
     */
    function approve(address spender, uint256 amount)
        public
        virtual
        override
        returns (bool)
    {
        address owner = _msgSender();
        _approve(owner, spender, amount);
        return true;
    }

    /**
     * @dev See {IERC20-transferFrom}.
     *
     * Emits an {Approval} event indicating the updated allowance. This is not
     * required by the EIP. See the note at the beginning of {ERC20}.
     *
     * NOTE: Does not update the allowance if the current allowance
     * is the maximum `uint256`.
     *
     * Requirements:
     *
     * - `from` and `to` cannot be the zero address.
     * - `from` must have a balance of at least `amount`.
     * - the caller must have allowance for ``from``'s tokens of at least
     * `amount`.
     */
    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) public virtual override returns (bool) {
        address spender = _msgSender();
        _spendAllowance(from, spender, amount);
        _transfer(from, to, amount);
        return true;
    }

    /**
     * @dev Atomically increases the allowance granted to `spender` by the caller.
     *
     * This is an alternative to {approve} that can be used as a mitigation for
     * problems described in {IERC20-approve}.
     *
     * Emits an {Approval} event indicating the updated allowance.
     *
     * Requirements:
     *
     * - `spender` cannot be the zero address.
     */
    function increaseAllowance(address spender, uint256 addedValue)
        public
        virtual
        returns (bool)
    {
        address owner = _msgSender();
        _approve(owner, spender, _allowances[owner][spender] + addedValue);
        return true;
    }

    /**
     * @dev Atomically decreases the allowance granted to `spender` by the caller.
     *
     * This is an alternative to {approve} that can be used as a mitigation for
     * problems described in {IERC20-approve}.
     *
     * Emits an {Approval} event indicating the updated allowance.
     *
     * Requirements:
     *
     * - `spender` cannot be the zero address.
     * - `spender` must have allowance for the caller of at least
     * `subtractedValue`.
     */
    function decreaseAllowance(address spender, uint256 subtractedValue)
        public
        virtual
        returns (bool)
    {
        address owner = _msgSender();
        uint256 currentAllowance = _allowances[owner][spender];
        require(
            currentAllowance >= subtractedValue,
            "ERC20: decreased allowance below zero"
        );
        unchecked {
            _approve(owner, spender, currentAllowance - subtractedValue);
        }

        return true;
    }

    function _plus(uint72 a, uint72 b) internal pure returns (uint72) {
        return a + b;
    }

    function _minus(uint72 a, uint72 b) internal pure returns (uint72) {
        return a - b;
    }

    function _delegationMove(
        uint104 userBalanceBefore,
        uint104 userBalanceAfter,
        address votingDelegate,
        address propositionDelegate,
        function(uint72, uint72) returns (uint72) operation
    ) internal {
        address delegate1Address = votingDelegate != address(0)
            ? votingDelegate
            : propositionDelegate;
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
        if (votingDelegate == propositionDelegate) {
            delegate1State.delegatedVotingBalance = operation(
                delegate1State.delegatedVotingBalance,
                delegationDelta
            );
            delegate1State.delegatedPropositionBalance = operation(
                delegate1State.delegatedPropositionBalance,
                delegationDelta
            );
        } else if (votingDelegate != address(0)) {
            delegate1State.delegatedVotingBalance = operation(
                delegate1State.delegatedVotingBalance,
                delegationDelta
            );
            if (propositionDelegate != address(0)) {
                _balances[propositionDelegate]
                    .delegatedPropositionBalance = operation(
                    _balances[propositionDelegate].delegatedPropositionBalance,
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
    ) internal virtual {
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

        emit Transfer(from, to, amount);
    }

    function _getDelegaties(
        address user,
        DelegationAwareBalance memory userState
    ) internal view returns (address, address) {
        return (
            userState.delegatingVoting ? _votingDelegateV2[user] : address(0),
            userState.delegatingProposition
                ? _propositionDelegateV2[user]
                : address(0)
        );
    }

    function delegateByType(address delegatee, DelegationType delegationType)
        external
        virtual
        override
    {
        DelegationAwareBalance memory userState = _balances[msg.sender];
        (
            address votingPowerDelegatee,
            address propositionPowerDelegatee
        ) = _getDelegaties(msg.sender, userState);

        //if user will delegate to self - then cleanup
        bool willDelegateAfter = delegatee != msg.sender &&
            delegatee != address(0);

        if (delegationType == DelegationType.VOTING_POWER) {
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
                _votingDelegateV2[msg.sender] = delegatee;
                _delegationMove(
                    userState.balance,
                    0,
                    delegatee,
                    address(0),
                    _plus
                );
            }
            if (willDelegateAfter != userState.delegatingVoting) {
                _balances[msg.sender].delegatingVoting = willDelegateAfter;
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
                _propositionDelegateV2[msg.sender] = delegatee;
                _delegationMove(
                    userState.balance,
                    0,
                    address(0),
                    delegatee,
                    _plus
                );
            }
            if (willDelegateAfter != userState.delegatingProposition) {
                _balances[msg.sender].delegatingProposition = willDelegateAfter;
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
            address votingPowerDelegatee,
            address propositionPowerDelegatee
        ) = _getDelegaties(msg.sender, userState);

        //if user will delegate to self - then cleanup
        bool willDelegateAfter = delegatee != msg.sender &&
            delegatee != address(0);

        _delegationMove(
            userState.balance,
            0,
            votingPowerDelegatee != delegatee
                ? votingPowerDelegatee
                : address(0),
            propositionPowerDelegatee != delegatee
                ? propositionPowerDelegatee
                : address(0),
            _minus
        );

        if (willDelegateAfter) {
            _votingDelegateV2[msg.sender] = delegatee;
            _propositionDelegateV2[msg.sender] = delegatee;
            _delegationMove(
                userState.balance,
                0,
                votingPowerDelegatee != delegatee ? delegatee : address(0),
                propositionPowerDelegatee != delegatee ? delegatee : address(0),
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
    }

    function getDelegateeByType(
        address delegator,
        DelegationType delegationType
    ) external view override returns (address) {
        return
            delegationType == DelegationType.VOTING_POWER
                ? _votingDelegateV2[delegator]
                : _propositionDelegateV2[delegator];
    }

    function getPowerCurrent(address user, DelegationType delegationType)
        external
        view
        override
        returns (uint256)
    {
        DelegationAwareBalance memory userState = _balances[user];
        uint256 userOwnPower = (delegationType == DelegationType.VOTING_POWER &&
            !userState.delegatingVoting) ||
            (delegationType == DelegationType.VOTING_POWER &&
                !userState.delegatingProposition)
            ? _balances[user].balance
            : 0;
        uint256 userDelegatedPower = (
            delegationType == DelegationType.VOTING_POWER
                ? _balances[user].delegatedVotingBalance
                : _balances[user].delegatedPropositionBalance
        ) * DELEGATED_POWER_DIVIDER;
        return userOwnPower + userDelegatedPower * DELEGATED_POWER_DIVIDER;
    }

    /**
     * @dev Moves `amount` of tokens from `sender` to `recipient`.
     *
     * This internal function is equivalent to {transfer}, and can be used to
     * e.g. implement automatic token fees, slashing mechanisms, etc.
     *
     * Emits a {Transfer} event.
     *
     * Requirements:
     *
     * - `from` cannot be the zero address.
     * - `to` cannot be the zero address.
     * - `from` must have a balance of at least `amount`.
     */
    function _transfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");

        _beforeTokenTransfer(from, to, amount);
        _transferWithDelegation(from, to, amount);
        _afterTokenTransfer(from, to, amount);
    }

    /** @dev Creates `amount` tokens and assigns them to `account`, increasing
     * the total supply.
     *
     * Emits a {Transfer} event with `from` set to the zero address.
     *
     * Requirements:
     *
     * - `account` cannot be the zero address.
     */
    function _mint(address account, uint256 amount) internal virtual {
        require(account != address(0), "ERC20: mint to the zero address");
        uint256 totalSupplyAfter = _totalSupply + amount;

        require( // TODO: think, should we have it or not
            totalSupplyAfter <= type(uint104).max,
            "ERC20: mint will end in uint104 overflow"
        );

        _beforeTokenTransfer(address(0), account, amount);

        _totalSupply = totalSupplyAfter;
        _transferWithDelegation(address(0), account, amount);

        _afterTokenTransfer(address(0), account, amount);
    }

    /**
     * @dev Destroys `amount` tokens from `account`, reducing the
     * total supply.
     *
     * Emits a {Transfer} event with `to` set to the zero address.
     *
     * Requirements:
     *
     * - `account` cannot be the zero address.
     * - `account` must have at least `amount` tokens.
     */
    function _burn(address account, uint256 amount) internal virtual {
        require(account != address(0), "ERC20: burn from the zero address");

        _beforeTokenTransfer(account, address(0), amount);
        // todo: I think that this case covered by _transferWithDelegation
        //        require(
        //            _balances[account].balance >= amount,
        //            "ERC20: burn amount exceeds balance"
        //        );

        _totalSupply -= amount;
        _transferWithDelegation(account, address(0), amount);

        _afterTokenTransfer(account, address(0), amount);
    }

    /**
     * @dev Sets `amount` as the allowance of `spender` over the `owner` s tokens.
     *
     * This internal function is equivalent to `approve`, and can be used to
     * e.g. set automatic allowances for certain subsystems, etc.
     *
     * Emits an {Approval} event.
     *
     * Requirements:
     *
     * - `owner` cannot be the zero address.
     * - `spender` cannot be the zero address.
     */
    function _approve(
        address owner,
        address spender,
        uint256 amount
    ) internal virtual {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }

    /**
     * @dev Spend `amount` form the allowance of `owner` toward `spender`.
     *
     * Does not update the allowance amount in case of infinite allowance.
     * Revert if not enough allowance is available.
     *
     * Might emit an {Approval} event.
     */
    function _spendAllowance(
        address owner,
        address spender,
        uint256 amount
    ) internal virtual {
        uint256 currentAllowance = allowance(owner, spender);
        if (currentAllowance != type(uint256).max) {
            require(
                currentAllowance >= amount,
                "ERC20: insufficient allowance"
            );
            unchecked {
                _approve(owner, spender, currentAllowance - amount);
            }
        }
    }

    /**
     * @dev Hook that is called before any transfer of tokens. This includes
     * minting and burning.
     *
     * Calling conditions:
     *
     * - when `from` and `to` are both non-zero, `amount` of ``from``'s tokens
     * will be transferred to `to`.
     * - when `from` is zero, `amount` tokens will be minted for `to`.
     * - when `to` is zero, `amount` of ``from``'s tokens will be burned.
     * - `from` and `to` are never both zero.
     *
     * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual {}

    /**
     * @dev Hook that is called after any transfer of tokens. This includes
     * minting and burning.
     *
     * Calling conditions:
     *
     * - when `from` and `to` are both non-zero, `amount` of ``from``'s tokens
     * has been transferred to `to`.
     * - when `from` is zero, `amount` tokens have been minted for `to`.
     * - when `to` is zero, `amount` of ``from``'s tokens have been burned.
     * - `from` and `to` are never both zero.
     *
     * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
     */
    function _afterTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual {}

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
