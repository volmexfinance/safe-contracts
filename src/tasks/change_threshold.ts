import "hardhat-deploy";
import "@nomiclabs/hardhat-ethers";
import { task } from "hardhat/config";

task("change-threshold", "Adds signer to safe")
    .addParam("module", "Address to module")
    .addParam("threshold", "New threshold for safe")
    .setAction(async (taskArgs, hre) => {
        const safeContract = await hre.ethers.getContractAt("RelayerHub", taskArgs.module);
        await safeContract.changeThreshold(taskArgs.threshold);
    });

export {};
