// SPDX-License-Identifier: GPL-3.0
// REMILIA COLLECTIVE

pragma solidity ^0.8.4;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract GeneralizedBonkler is ERC721, Ownable {

    address internal _minter;
    uint32 public nextTokenId;

	constructor(string memory name, string memory symbol) ERC721(name, symbol) {
        nextTokenId = 1;
    }

    function mint() external payable onlyMinter returns (uint256 tokenId) {
        // require(!mintLocked, "Locked."); TODO handled by Archetype contract
        tokenId = nextTokenId++;
        _mint(msg.sender, tokenId); // Mint the sender 1 token.
    }

    function setMinter(address minter) external onlyOwner {
        // require(!minterLocked, "Locked."); TODO handled by Archetype contract
        _minter = minter;
    }

    /**
     * @dev Guards a function such that only the minter is authorized to call it.
     */
    modifier onlyMinter() virtual {
        require(msg.sender == _minter, "Unauthorized minter.");
        _;
    }
}
