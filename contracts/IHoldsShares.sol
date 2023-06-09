// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.4;

interface IHoldsShares {

	/**
	 * @param updater Should be an IRewardClaimer.
	 */
	function addSharesUpdater(address updater) external;

	/**
	 * @dev An IRewardClaimer will use this function to calculate rewards for
	 * a bidder.
	 */
	function getAndClearSharesFor(address user) external returns (uint256);

	function getTokenShares(address user) external view returns (uint256);

	function getIsSharesUpdater(address updater) external view returns (bool);

}

