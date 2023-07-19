// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity >=0.7.0 <0.9.0;

enum Operation {
    Call,
    DelegateCall
}

/**
 * @title ISafeSigner - An interface to help execute transaction on safe from a module
 */
interface ISafeSigner{
    /**
     * @notice Sets an initial storage of the Safe contract.
     * @dev exec transaction from a module 
     * @param to Destination address of module transaction.
     * @param value Ether value of module transaction.
     * @param data Data payload of module transaction.
     * @param operation Operation type of module transaction.
     * @return success Boolean flag indicating if the call succeeded.
    */
    function execTransactionFromModule(
        address to,
        uint256 value,
        bytes memory data,
        Operation operation
    ) external returns (bool success);
}