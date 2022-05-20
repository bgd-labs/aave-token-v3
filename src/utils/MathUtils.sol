// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

library MathUtils {
    function plus(uint72 a, uint72 b) internal pure returns (uint72) {
        return a + b;
    }

    function minus(uint72 a, uint72 b) internal pure returns (uint72) {
        return a - b;
    }
}
