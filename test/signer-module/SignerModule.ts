import { AddressOne } from './../../src/utils/constants';
import hre, { deployments, ethers, waffle } from "hardhat";
import "@nomiclabs/hardhat-ethers";
import { expect } from "chai";
import { getSafeTemplate, getSafeWithOwners } from "../utils/setup";
import { executeContractCallWithSigners } from "../../src/utils/execution";
import { AddressOne } from "../../src";

describe("Add Signer Module", async () => {
    const [user1, user2, user3, user4, user5, user6, user7] = waffle.provider.getWallets();

    const setupTests = deployments.createFixture(async ({ deployments }) => {
        await deployments.fixture();
        const signerModule = await ethers.getContractFactory("RelayerHub");
        const safe = await getSafeWithOwners([user1.address, user2.address, user3.address, user4.address, user5.address])
        const signerModuleContract = await signerModule.deploy(safe.address, user7.address);
        await executeContractCallWithSigners(
            safe,
            safe,
            "enableModule",
            [signerModuleContract.address],
            [user1, user2, user3, user4, user5],
        );
        return {
            template: await getSafeTemplate(),
            safe,
            signerModuleContract,
        };
    });

    it("should add signer by module", async () => {
        const { safe, signerModuleContract } = await setupTests();
        await signerModuleContract.connect(user7).addOwner(user6.address, 5);
        await expect((await safe.getOwners())[0]).to.equal(user6.address);
    });

    it("should remove signer by module", async () => {
        const { safe, signerModuleContract } = await setupTests();
        await signerModuleContract.connect(user7).addOwner(user6.address, 5);
        await expect(await safe.isOwner(user6.address)).to.equal(true);
        await signerModuleContract.connect(user7).removeOwner(AddressOne, user6.address, 3);
        await expect(await safe.isOwner(user6.address)).to.equal(false);
    });

    it("should change threshold by module", async () => {
        const { safe, signerModuleContract } = await setupTests();
        await signerModuleContract.connect(user7).changeThreshold(3);
        await expect(await safe.getThreshold()).to.equal(3);
    });

    it("should change add manager to module", async () => {
        const { safe, signerModuleContract } = await setupTests();
        await signerModuleContract.connect(user7).addManager(user1.address);
        await signerModuleContract.connect(user1).addOwner(user6.address, 5);
        await expect(await safe.isOwner(user6.address)).to.equal(true);
    });

    it("should add signer by module with task", async () => {
        const { safe, signerModuleContract } = await setupTests();
        await hre.run("add-signer", {
            module: signerModuleContract.address,
            signer: user7.address,
            threshold: "6",
        });
        await expect((await safe.getOwners())[0]).to.equal(user7.address);
    });

    it("should remove signer by module with task", async () => {
        const { safe, signerModuleContract } = await setupTests();
        await signerModuleContract.connect(user7).addOwner(user6.address, 5);
        await expect(await safe.isOwner(user6.address)).to.equal(true);
        await hre.run("remove-signer", {
            module: signerModuleContract.address,
            remover: AddressOne,
            signer: user6.address,
            threshold: "3",
        });
        await expect(await safe.isOwner(user6.address)).to.equal(false);
    });

    it("should change threshold by module with task", async () => {
        const { safe, signerModuleContract } = await setupTests();
        await hre.run("change-threshold", {
            module: signerModuleContract.address,
            threshold: "4",
        });
        await expect(await safe.getThreshold()).to.equal(4);
    });
});
