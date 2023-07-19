import { deployments, ethers, waffle } from "hardhat";
import "@nomiclabs/hardhat-ethers";
import { expect } from "chai";
import { getSafeTemplate, getSafeWithOwners } from "../utils/setup";
import { executeContractCallWithSigners } from "../../src/utils/execution";

describe("Add Signer Module", async () => {
    const [user1, user2, user3, user4, user5, user6, user7] = waffle.provider.getWallets();

    const setupTests = deployments.createFixture(async ({ deployments }) => {
        await deployments.fixture();
        return {
            template: await getSafeTemplate(),
            safe: await getSafeWithOwners([user1.address, user2.address, user3.address, user4.address, user5.address]),
        };
    });

    it("should add signer by module", async () => {
        const { safe } = await setupTests();
        const signerModule = await ethers.getContractFactory("SignerModule");
        const SignerModuleContract = await signerModule.deploy(safe.address, user7.address);
        await executeContractCallWithSigners(
            safe,
            safe,
            "enableModule",
            [SignerModuleContract.address],
            [user1, user2, user3, user4, user5],
        );
        /* await expect(
            await SignerModuleContract.connect(user7).addSigner(
                await safe.interface.encodeFunctionData("addOwnerWithThreshold", [user6.address, 5]),
            ),
        ); */
        await SignerModuleContract.connect(user7).addSigner(user6.address, 5);
        await expect((await safe.getOwners())[0]).to.equal(user6.address);
    });
});
