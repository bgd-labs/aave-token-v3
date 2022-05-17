// SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import {DSTest} from "../../../lib/ds-test/src/test.sol";

import {VM} from "./VM.sol";
import {console} from "./console.sol";

contract BaseTest is DSTest {
    VM internal constant vm = VM(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
}
