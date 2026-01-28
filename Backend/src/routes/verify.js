import express from "express";
import multer from "multer";
import { generateHash } from "../services/hash.service.js";
import { analyzeFile } from "../services/ml.service.js";
import { storeOnChain } from "../services/blockchain.service.js";

const router = express.Router();

// 🔥 multer memory storage (IMPORTANT)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }
});

router.post("/", upload.single("file"), async (req, res) => {
  console.log("📨 /verify hit");

  if (!req.file) {
    return res.status(400).json({ error: "No file uploaded" });
  }

  try {
    const fileBuffer = req.file.buffer;

    // Generate hash
    const hashHex = generateHash(fileBuffer);
    const hashBytes32 = "0x" + hashHex;

    // Analyze with ML API (with timeout)
    let mlResult;
    try {
      mlResult = await Promise.race([
        analyzeFile(fileBuffer),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error("ML API timeout")), 30000)
        )
      ]);
    } catch (mlErr) {
      console.error("⚠️ ML Service error:", mlErr.message);
      return res.status(503).json({
        error: "ML analysis service unavailable",
        hash: hashHex
      });
    }

    // Store on blockchain (with timeout)
    let txHash;
    try {
      txHash = await Promise.race([
        storeOnChain(
          hashBytes32,
          mlResult.aiGenerated,
          Math.floor(mlResult.score * 100)
        ),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error("Blockchain timeout")), 60000)
        )
      ]);
    } catch (chainErr) {
      console.error("⚠️ Blockchain error:", chainErr.message);
      return res.status(503).json({
        error: "Blockchain service unavailable",
        hash: hashHex,
        aiGenerated: mlResult.aiGenerated,
        confidence: mlResult.score
      });
    }

    res.json({
      hash: hashHex,
      aiGenerated: mlResult.aiGenerated,
      confidence: mlResult.score,
      blockchainTx: txHash
    });

  } catch (err) {
    console.error("❌ VERIFY ERROR:", err);
    res.status(500).json({ error: err.message || "Verification failed" });
  }
});

export default router;
