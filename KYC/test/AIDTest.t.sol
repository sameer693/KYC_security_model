// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import {AdvancedIdentityVerification} from "../src/AID.sol";
import {LinkTokenInterface} from "@chainlink/contracts/v0.8/interfaces/LinkTokenInterface.sol";
import {Chainlink, ChainlinkClient} from "@chainlink/contracts/v0.8/ChainlinkClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/v0.8/dev/ConfirmedOwner.sol";

contract AdvancedIdentityVerificationTest is Test,ChainlinkClient {
    using Chainlink for Chainlink.Request;
    AdvancedIdentityVerification aid;
    LinkTokenInterface link;

    function setUp() public {
        aid = new AdvancedIdentityVerification();
        link = LinkTokenInterface(chainlinkTokenAddress());
    }

    function testRequestValueData() public {
        string memory path = "some/path";
        bytes32 requestId = aid.requestMultipleParameters(path);
        // Check if the requestId is not zero
        assert(requestId != bytes32(0));
    }

    function testFulfill() public {
        string memory path = "some/path";
        bytes32 requestId = keccak256(abi.encodePacked(this, block.timestamp));
        uint256 value = 100;
        aid.fulfillMultipleParameters(requestId, value);
    
        // Check if the value is set correctly for the path
        assertEq(aid.verifyAddress(path), value);
    }

    function testWithdrawLink() public {
        // Assume the contract has some LINK tokens for testing
        uint256 initialBalance = 1 * 10 ** 18; // 1 LINK

        // Transfer some LINK to the contract for testing
        deal(address(link), address(aid), initialBalance);

        // Withdraw LINK from the contract
        aid.withdrawLink();

        // Check if the balance of the contract is zero after withdrawal
        assertEq(link.balanceOf(address(aid)), 0);

        // Check if the balance of the test contract (msg.sender) is equal to the withdrawn amount
        assertEq(link.balanceOf(address(this)), initialBalance);
    }
}