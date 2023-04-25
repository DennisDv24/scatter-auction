// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.4;

import "@openzeppelin/contracts/access/Ownable.sol";
import "solady/src/utils/MerkleProofLib.sol";

contract ScatterAuctionBoosterStorage is Ownable {

	bytes32 public root;

	function setRoot(bytes32 _root) public onlyOwner {
		root = _root;
	}

	function isValid(
		bytes32[] memory proof, address bidder, uint16 rewardableTokensHeld
	) public returns (bool) {
		require(root > 0, "Merkle root not initialized.");
		return MerkleProofLib.verify(
			proof,
			root,
			keccak256(abi.encodePacked(bidder, rewardableTokensHeld))
		);
	}

}
