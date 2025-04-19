// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ZakatGovernanceToken
 * @dev Non-tradable ERC20 token for Zakat DAO governance
 * Tokens can only be minted by owner and transfers are restricted
 */
contract ZakatGovernanceToken is ERC20, Ownable {
    // Mapping to track approved contracts that can transfer tokens
    mapping(address => bool) public approvedContracts;
    
    // Events for monitoring token operations
    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);
    event TransferRestricted(address indexed from, address indexed to, uint256 amount);
    event ContractApprovalUpdated(address indexed contractAddress, bool approved);

    /**
     * @dev Constructor initializes the token with name and symbol
     */
    constructor() ERC20("ZakatGovernanceToken", "ZGT") {
        // No initial supply minted - tokens will be minted as donations are made
    }

    /**
     * @dev Modifier to check if transfer is allowed
     * Only owner and approved contracts can transfer tokens
     */
    modifier canTransfer() {
        require(
            _msgSender() == owner() || approvedContracts[_msgSender()],
            "ZGT: transfers restricted to owner and approved contracts"
        );
        _;
    }

    /**
     * @dev Mint new tokens - only callable by owner
     * @param to Address to mint tokens to
     * @param amount Amount of tokens to mint
     */
    function mint(address to, uint256 amount) public onlyOwner {
        require(to != address(0), "ZGT: mint to zero address");
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    /**
     * @dev Burn tokens - only callable by owner
     * @param from Address to burn tokens from
     * @param amount Amount of tokens to burn
     */
    function burn(address from, uint256 amount) public onlyOwner {
        _burn(from, amount);
        emit TokensBurned(from, amount);
    }

    /**
     * @dev Add or remove contract from approved transfers list
     * @param contractAddress Address of contract to approve/disapprove
     * @param approved Approval status to set
     */
    function setContractApproval(address contractAddress, bool approved) public onlyOwner {
        require(contractAddress != address(0), "ZGT: approve zero address");
        approvedContracts[contractAddress] = approved;
        emit ContractApprovalUpdated(contractAddress, approved);
    }

    /**
     * @dev Override transfer function to enforce restrictions
     */
    function transfer(address to, uint256 amount) public virtual override canTransfer returns (bool) {
        return super.transfer(to, amount);
    }

    /**
     * @dev Override transferFrom function to enforce restrictions
     */
    function transferFrom(address from, address to, uint256 amount) public virtual override canTransfer returns (bool) {
        return super.transferFrom(from, to, amount);
    }

    /**
     * @dev Returns the number of decimals for token precision
     * Override to use 0 decimals since this is a governance token
     */
    function decimals() public pure override returns (uint8) {
        return 0;
    }
}
