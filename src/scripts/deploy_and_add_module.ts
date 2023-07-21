import { AddressZero } from '@ethersproject/constants';
import { AddressOne } from './../utils/constants';
import { ethers } from 'hardhat';
import { Wallet, providers } from 'ethers';
import { HardhatRuntimeEnvironment } from "hardhat/types";
import { EIP712_SAFE_TX_TYPE, executeContractCallWithSigners } from "./../utils/execution";

const deployHub = async function deploySigner() {
    const hubF= await ethers.getContractFactory("RelayerHub");
    const hub = await hubF.deploy("SafeAddress", "HubManagerAddress");
    const safe = await ethers.getContractAt("SafeL2", "<safeAddress>");
    const prov = new providers.JsonRpcProvider("RPC");
    const signer1 = new ethers.Wallet("<privateKey>", prov);
    //console.log(await hub.changeSafe(safe.address));
    console.log(hub.address);
    //const data = await safe.interface.encodeFunctionData("enableModule", ["module address"]);
    //const contractF = await ethers.getContractFactory("SafeL2");
    //const safe = await contractF.deploy();
    //console.log(safe);
    //const signedData = await signer._signTypedData({ verifyingContract: safe.address, chainId:  }, EIP712_SAFE_TX_TYPE, data);
    /* console.log(
        await executeContractCallWithSigners(safe, safe, "enableModule", ["<addressofModule></addressofModule>"], [signer1]),
    ); */
    console.log(await safe.getOwners());
    /* console.log()
    console.log(signer1.address); */
    console.log(await safe.setup([signer1.address], 1, AddressZero, "0x", AddressZero, AddressZero, 0, AddressZero));
};
deployHub();
