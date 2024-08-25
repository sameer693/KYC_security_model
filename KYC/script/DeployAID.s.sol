// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "forge-std/Script.sol";
import "../src/AID.sol";

contract DeployAID is Script {
    function run() external {
        vm.startBroadcast();

        // Deploy the MultiWordConsumer contract
        new AdvancedIdentityVerification();

        vm.stopBroadcast();
    }
}