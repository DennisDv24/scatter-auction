// SPDX-License-Identifier: GPL-3.0
// REMILIA COLLECTIVE

pragma solidity ^0.8.4;

import "solady/src/utils/SafeTransferLib.sol";
import "solady/src/utils/LibString.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract GeneralizedBonkler is ERC721, Ownable {
    using LibString for string;

    uint256 public constant START_TOKEN_ID = 1;

    string internal __baseURI;

    // @dev The Bonkler auction contract.
    address internal _minter;
    uint32 public nextTokenId;

    // @dev Whether the minter is permanently locked.
    bool public minterLocked;

    bool public mintLocked;
    bool public baseURILocked;

    mapping(uint256 => uint256) internal _tokenShares;

    // @dev Mapping of `tokenId` to the generation hash for each Bonkler.
    mapping(uint256 => uint256) internal _tokenGenerationHash;

    constructor() ERC721("Bonkler", "BNKLR") {
        nextTokenId = uint32(START_TOKEN_ID);
    }

    /*´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*/
    /*              PUBLIC / EXTERNAL VIEW FUNCTIONS              */
    /*.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*/

    function tokenURI(uint256 tokenId)
        public
        view
        override
        returns (string memory result)
    {
        require(_exists(tokenId), "Token does not exist.");

        result = __baseURI;
        if (bytes(result).length != 0) {
            result = result.replace("{id}", LibString.toString(tokenId));
            result = result.replace("{shares}", LibString.toString(_tokenShares[tokenId]));
            result = result.replace("{hash}", LibString.toString(_tokenGenerationHash[tokenId]));
        }
    }

    function getBonklerShares(uint256 tokenId) public view returns (uint256) {
        return _tokenShares[tokenId];
    }

    function getBonklerHash(uint256 tokenId) external view returns (uint256) {
        return _tokenGenerationHash[tokenId];
    }

    function totalSupply() external view returns (uint256) {
        return nextTokenId - START_TOKEN_ID;
    }

    function exists(uint256 tokenId) external view returns (bool) {
        return _ownerOf(tokenId) != address(0);
    }

    function exist(uint256[] memory tokenIds) external view returns (bool[] memory results) {
        uint256 n = tokenIds.length;
        results = new bool[](n);
        for (uint256 i; i < n; ++i) {
            results[i] = _ownerOf(tokenIds[i]) != address(0);
        }
    }

    function tokensOfOwner(address owner) external view returns (uint256[] memory tokenIds) {
        uint256 n = balanceOf(owner);
        tokenIds = new uint256[](n);
        uint256 end = nextTokenId;
        uint256 o;
        for (uint256 i = START_TOKEN_ID; i < end && o < n; ++i) {
            if (_ownerOf(i) == owner) tokenIds[o++] = i;
        }
    }

    /*´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*/
    /*                   MINTER WRITE FUNCTIONS                   */
    /*.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*/

    function transferPurchasedBonkler(uint256 tokenId, address to) external payable onlyMinter {
        _tokenShares[tokenId] = msg.value;
        _transfer(msg.sender, to, tokenId);
    }

    function mint() external payable onlyMinter returns (uint256 tokenId) {
        require(!mintLocked, "Locked.");
        tokenId = nextTokenId++;
        _mint(msg.sender, tokenId); // Mint the sender 1 token.
    }

    /*´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*/
    /*                   ADMIN WRITE FUNCTIONS                    */
    /*.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*/

    function setMinter(address minter) external onlyOwner {
        require(!minterLocked, "Locked.");
        _minter = minter;
    }

    function setBaseURI(string memory baseURI) external onlyOwner {
        require(!baseURILocked, "Locked.");
        __baseURI = baseURI;
    }

    function lockMinter() external onlyOwner {
        minterLocked = true;
    }

    function lockMint() external onlyOwner {
        mintLocked = true;
    }

    function lockBaseURI() external onlyOwner {
        baseURILocked = true;
    }

    /*´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*/
    /*                 INTERNAL / PRIVATE HELPERS                 */
    /*.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*/

    /**
     * @dev Guards a function such that only the minter is authorized to call it.
     */
    modifier onlyMinter() virtual {
        require(msg.sender == _minter, "Unauthorized minter.");
        _;
    }
}
