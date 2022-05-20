// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IGovernancePowerDelegationToken {
    enum GovernancePowerType {
        VOTING,
        PROPOSITION
    }

    /**
     * @dev emitted when a user delegates to another
     * @param delegator the delegator
     * @param delegatee the delegatee
     * @param delegationType the type of delegation (VOTING, PROPOSITION)
     **/
    event DelegateChanged(
        address indexed delegator,
        address indexed delegatee,
        GovernancePowerType delegationType
    );

    /**
     * @dev emitted when an action changes the delegated power of a user
     * @param user the user which delegated power has changed
     * @param amount the amount of delegated power for the user
     * @param delegationType the type of delegation (VOTING, PROPOSITION)
     **/
    event DelegatedPowerChanged(
        address indexed user,
        uint256 amount,
        GovernancePowerType delegationType
    );

    /**
     * @dev delegates the specific power to a delegatee
     * @param delegatee the user which delegated power has changed
     * @param delegationType the type of delegation (VOTING, PROPOSITION)
     **/
    function delegateByType(
        address delegatee,
        GovernancePowerType delegationType
    ) external;

    /**
     * @dev delegates all the powers to a specific user
     * @param delegatee the user to which the power will be delegated
     **/
    function delegate(address delegatee) external;

    /**
     * @dev returns the delegatee of an user
     * @param delegator the address of the delegator
     **/
    function getDelegateeByType(
        address delegator,
        GovernancePowerType delegationType
    ) external view returns (address);

    /**
     * @dev returns the current voting or proposition power of a user.
     * @param user the user
     * @param delegationType the type of delegation (VOTING, PROPOSITION)
     **/
    function getPowerCurrent(address user, GovernancePowerType delegationType)
        external
        view
        returns (uint256);
}
