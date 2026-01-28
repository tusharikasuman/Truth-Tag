import { ethers } from "ethers";
import dotenv from "dotenv";

dotenv.config();

const CONTRACT_ABI = [
  {
    "inputs": [
      { "internalType": "bytes32", "name": "_hash", "type": "bytes32" },
      { "internalType": "bool", "name": "_aiGenerated", "type": "bool" },
      { "internalType": "uint256", "name": "_confidence", "type": "uint256" }
    ],
    "name": "storeRecord",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
];

let provider, wallet, contract;

const initializeBlockchain = () => {
  try {
    if (!process.env.RPC_URL || !process.env.PRIVATE_KEY || !process.env.CONTRACT_ADDRESS) {
      throw new Error(
        "Missing blockchain config: RPC_URL, PRIVATE_KEY, or CONTRACT_ADDRESS"
      );
    }

    provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
    wallet = new ethers.Wallet(process.env.PRIVATE_KEY.trim(), provider);
    contract = new ethers.Contract(
      process.env.CONTRACT_ADDRESS,
      CONTRACT_ABI,
      wallet
    );

    console.log("✅ Blockchain initialized successfully");
    return true;
  } catch (err) {
    console.error("❌ Blockchain initialization failed:", err.message);
    return false;
  }
};

export const storeOnChain = async (hash, aiGenerated, confidence) => {
  // For testing/development: return mock transaction if blockchain not configured
  if (!process.env.RPC_URL || process.env.RPC_URL.includes("YOUR_")) {
    console.log("⚠️  Blockchain not configured - returning mock transaction");
    return "0x" + Array(64).fill(0).map(() => Math.floor(Math.random() * 16).toString(16)).join("");
  }

  if (!contract) {
    if (!initializeBlockchain()) {
      throw new Error("Blockchain not configured");
    }
  }

  try {
    console.log("📝 Attempting to store record on blockchain...");
    console.log("   Hash:", hash);
    console.log("   AI Generated:", aiGenerated);
    console.log("   Confidence:", confidence);

    const tx = await contract.storeRecord(hash, aiGenerated, confidence);
    console.log("✅ Transaction sent:", tx.hash);

    const receipt = await tx.wait();
    console.log("✅ Transaction confirmed:", receipt.transactionHash);

    return tx.hash;
  } catch (err) {
    console.error("❌ Blockchain transaction error:", err.message);
    throw new Error(`Blockchain error: ${err.message}`);
  }
};
