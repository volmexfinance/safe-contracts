// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity >=0.7.0 <0.9.0;

import "./ISafeSigner.sol";

/**
 * @title SignerModule - A module that helps add signer
 * @dev Most important concepts:
 *      - Threshold: Number of required confirmations for a Safe transaction.
 *      - Owners: List of addresses that control the Safe. They are the only ones that can add/remove owners, change the threshold and
 *        approve transactions. Managed in `OwnerManager`.
 * @author Aditya Rout - @aditya-volmex
 */
contract SignerModule {
    
    ISafeSigner public immutable safeL2;
    address public immutable owner;

    /**
     * @notice Initializes this contract with address of safe and owners address
     * @param safe address of safe contract
     * @param _owner address of owner of of this contract
     */
    constructor(address safe, address _owner) {
        safeL2 = ISafeSigner(safe);
        owner = _owner;
    }

    /**
     * @notice Adds owner and sets new threshold for safe contract
     * @param signer New owner address.
     * @param threshold New threshold.
     * @return bool indicating whether transaction failed or not.
     */
    function addSigner(address signer, uint256 threshold) external returns (bool) {
        require(msg.sender == owner, "Sender must be owner");
        return safeL2.execTransactionFromModule(address(safeL2), 0, abi.encodeWithSignature("addOwnerWithThreshold(address,uint256)", signer, threshold), Operation.Call);
    }
}
