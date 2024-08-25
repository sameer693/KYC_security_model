//SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {Chainlink, ChainlinkClient} from "@chainlink/contracts/v0.8/ChainlinkClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/v0.8/dev/ConfirmedOwner.sol";
import {LinkTokenInterface} from "@chainlink/contracts/v0.8/interfaces/LinkTokenInterface.sol";

/**
 * Request testnet LINK and ETH here: https://faucets.chain.link/
 * Find information on LINK Token Contracts and get the latest ETH and LINK faucets here: https://docs.chain.link/docs/link-token-contracts/
 */


contract AdvancedIdentityVerification is ChainlinkClient, ConfirmedOwner {
    string walletID;
    mapping(string => uint256) public verifyAddress;
    using Chainlink for Chainlink.Request;


    uint256 value;
    bytes32 private jobId;
    uint256 private fee;

    event RequestMultipleFulfilled(
        bytes32 indexed requestId,
        uint256 value
    );

    /**
     * @notice Initialize the link token and target oracle
     * @dev The oracle address must be an Operator contract for multiword response
     *
     *
     * Sepolia Testnet details:
     * Link Token: 0x779877A7B0D9E8603169DdbD7836e478b4624789
     * Oracle: 0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD (Chainlink DevRel)
     * jobId: 53f9755920cd451a8fe46f5087468395
     *
     */
    constructor() ConfirmedOwner(msg.sender) {
        setChainlinkToken(0x779877A7B0D9E8603169DdbD7836e478b4624789);
        setChainlinkOracle(0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD);
        jobId = "7da2702f37fd48e5b1b9a5715e3509b6";
        fee = (1 * LINK_DIVISIBILITY) / 10; // 0,1 * 10**18 (Varies by network and job)
    }

    /**
     * @notice Request mutiple parameters from the oracle in a single transaction
     */
    function requestMultipleParameters(string memory _path) public returns (bytes32 requestId) {
        walletID = _path;
        Chainlink.Request memory req = buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfillMultipleParameters.selector
        );
        req.add(
            "get",
            "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=BTC"
        );
        req.add("path", _path);
        sendChainlinkRequest(req, fee); // MWR API.
    }

    /**
     * @notice Fulfillment function for multiple parameters in a single request
     * @dev This is called by the oracle. recordChainlinkFulfillment must be used.
     */
    function fulfillMultipleParameters(
        bytes32 _requestId,
        uint256 _value
    ) public recordChainlinkFulfillment(_requestId) {
        emit RequestMultipleFulfilled(
            _requestId,
            _value
        );
        value = _value;
        verifyAddress[walletID] = value;
    }

    /**
     * Allow withdraw of Link tokens from the contract
     */
    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer"
        );
    }
}
