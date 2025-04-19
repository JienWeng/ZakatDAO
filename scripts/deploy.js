const hre = require("hardhat");

async function main() {
  console.log("Deploying ZakatGovernanceToken...");
  
  const ZGT = await hre.ethers.getContractFactory("ZakatGovernanceToken");
  const zgt = await ZGT.deploy();
  await zgt.deployed();
  
  console.log("ZGT deployed to:", zgt.address);
  
  // Wait for few block confirmations
  await zgt.deployTransaction.wait(6);
  
  // Verify contract on Polygonscan
  console.log("Verifying contract...");
  await hre.run("verify:verify", {
    address: zgt.address,
    constructorArguments: [],
  });
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
