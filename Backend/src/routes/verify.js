import express from "express";
import multer from "multer";
import { generateHash } from "../services/hash.service.js";
import { analyzeFile } from "../services/ml.service.js";
import { storeOnChain } from "../services/blockchain.service.js";

const router = express.Router();
const upload = multer();

router.post("/", upload.single("file"), async (req, res) => {
  try {
    const fileBuffer = req.file.buffer;

    const hashHex = generateHash(fileBuffer);
    const hashBytes32 = "0x" + hashHex;

    const mlResult = await analyzeFile(fileBuffer);

    // 🔥 blockchain call
    const txHash = await storeOnChain(
      hashBytes32,
      mlResult.aiGenerated,
      Math.floor(mlResult.score * 100)
    );

    res.json({
      hash: hashHex,
      aiGenerated: mlResult.aiGenerated,
      confidence: mlResult.score,
      blockchainTx: txHash
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Verification failed" });
  }
});

export default router;
