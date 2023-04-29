// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

interface IRewardToken {
  	function mintFromAuctionHouse(address to, uint256 amount) external;
	function getRewardRatio() external returns (uint256);
}
