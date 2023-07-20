import "hardhat-deploy";
import "@nomiclabs/hardhat-ethers";
import { task } from "hardhat/config";

task("remove-signer", "Adds signer to safe")
    .addParam("module", "Address to module")
    .addParam("remover", "Address removing signer")
    .addParam("signer", "Address to add as signer")
    .addParam("threshold", "New threshold for safe")
    .setAction(async (taskArgs, hre) => {
        const safeContract = await hre.ethers.getContractAt("RelayerHub", taskArgs.module);
        await safeContract.removeOwner(taskArgs.remover, taskArgs.signer, taskArgs.threshold);
    });

export {};
