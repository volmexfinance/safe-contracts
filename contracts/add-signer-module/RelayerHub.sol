// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity >=0.7.0 <0.9.0;

import "./ISafeSigner.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title SignerModule - A module that helps add, remove signer and update threshold
 * @dev Most important concepts:
 *      - Threshold: Number of required confirmations for a Safe transaction.
 *      - Owners: List of addresses that control the Safe. They are the only ones that can add/remove owners, change the threshold and
 *        approve transactions. Managed in `OwnerManager`.
 * @author Aditya Rout - @aditya-volmex
 */
contract RelayerHub  is AccessControl{
    
    ISafeSigner public safeL2;
    bytes32 public constant  RELAYER_HUB_MANAGER = keccak256("RELAYER_HUB_MANAGER");

    /**
     * @notice Initializes this contract with address of safe and owners address
     * @param safe address of safe contract
     * @param _owner address of owner of of this contract
     */
    constructor(address safe, address _owner) {
        safeL2 = ISafeSigner(safe);
        _setupRole(RELAYER_HUB_MANAGER, _owner);
    }

    /**
     * @notice Adds owner and sets new threshold for safe contract
     * @param signer New owner address.
     * @param threshold New threshold.
     * @return bool indicating whether transaction failed or not.
     */
    function addOwner(address signer, uint256 threshold) external returns (bool) {
        hasRole(RELAYER_HUB_MANAGER, msg.sender);
        return safeL2.execTransactionFromModule(address(safeL2), 0, abi.encodeWithSignature("addOwnerWithThreshold(address,uint256)", signer, threshold), Operation.Call);
    }

    /**
     * @notice Removes owner and sets new threshold for safe contract
     * @param signerRemover Owner who is removing owner.
     * @param signerToBeRemoved Oner being removed.
     * @param threshold New threshold.
     * @return bool indicating whether transaction failed or not.
     */
    function removeOwner(address signerRemover, address signerToBeRemoved, uint256 threshold) external returns (bool) {
        hasRole(RELAYER_HUB_MANAGER, msg.sender);
        return safeL2.execTransactionFromModule(address(safeL2), 0, abi.encodeWithSignature("removeOwner(address,address,uint256)", signerRemover, signerToBeRemoved, threshold), Operation.Call);
    }

    /**
     * @notice Sets new threshold for safe contract
     * @param threshold New threshold.
     * @return bool indicating whether transaction failed or not.
     */
    function changeThreshold(uint256 threshold) external returns (bool) {
        hasRole(RELAYER_HUB_MANAGER, msg.sender);
        return safeL2.execTransactionFromModule(address(safeL2), 0, abi.encodeWithSignature("changeThreshold(uint256)",threshold), Operation.Call);
    }

    /**
     * @notice Updates address of the safe
     * @param _safe New safe.
     */
    function changeSafe(address _safe) external {
        hasRole(RELAYER_HUB_MANAGER, msg.sender);
        safeL2 = ISafeSigner(_safe);
    }

    /**
     * @notice Add Relayer Hub Manager.
     * @param manager address to be added as manager.
     */
    function addManager(address manager) external {
        hasRole(RELAYER_HUB_MANAGER, msg.sender);
        _setupRole(RELAYER_HUB_MANAGER, manager);
    }
}
