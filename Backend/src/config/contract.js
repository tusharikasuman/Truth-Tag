import { ethers } from "ethers";
import { CONTRACT_ADDRESS, CONTRACT_ABI } from "../config/contract.js";

const provider = new ethers.JsonRpcProvider(
  "http://127.0.0.1:8545"
); 
// 👆 Remix VM / local demo ke liye

const PRIVATE_KEY = "0xYOUR_PRIVATE_KEY";
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

const contract = new ethers.Contract(
  CONTRACT_ADDRESS,
  CONTRACT_ABI,
  wallet
);

export const storeOnChain = async (hash, aiGenerated, confidence) => {
  const tx = await contract.storeRecord(
    hash,
    aiGenerated,
    confidence
  );

  await tx.wait();

  return tx.hash;
};
