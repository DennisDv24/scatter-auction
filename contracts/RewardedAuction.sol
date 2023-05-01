// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.4;

import "./ScatterAuction.sol";

contract RewardedAuction is ScatterAuction {

	/**
     * @dev Amount of eth bidded by an address.
     */
    mapping(address => uint256) public rewardTokenShares;
	mapping(address => bool) public allowSharesUpdate;

	address public rewardToken;

    function createBid(uint256 nftId) override public payable {
		super.createBid(nftId);
		rewardTokenShares[msg.sender] += msg.value;
	}
	
	/**
	 * @param user Should be an IRewardToken.
	 */
	// TODO test msg.sender
	function getAndClearSharesFor(address user) public returns (uint256 shares) {
		require(msg.sender == owner() || allowSharesUpdate[msg.sender]);
		shares = rewardTokenShares[user];
		delete rewardTokenShares[user];
	}

	function addSharesUpdated(address updater) public onlyOwner {
		allowSharesUpdate[updater] = true;
	}

}
