import express from "express";
import cors from "cors";
import dotenv from "dotenv";

console.log("🔍 Starting server initialization...");

import verifyRoute from "./routes/verify.js";

console.log("✅ verifyRoute imported successfully");

dotenv.config();

console.log("✅ dotenv loaded");

const app = express();
const PORT = 3000;

console.log("✅ express app created");

// 🔥 log every request (debug)
app.use((req, res, next) => {
  console.log("➡️", req.method, req.originalUrl);
  next();
});

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// test route
app.post("/ping", (req, res) => {
  res.json({ ok: true });
});

// health check
app.get("/health", (req, res) => {
  res.json({ status: "healthy", timestamp: new Date().toISOString() });
});

// verify route
app.use("/verify", verifyRoute);

// global error handler
app.use((err, req, res, next) => {
  console.error("🔥 GLOBAL ERROR:", err);
  res.status(500).json({ error: err.message });
});

// Handle uncaught exceptions
process.on("unhandledRejection", (reason, promise) => {
  console.error("❌ Unhandled Rejection:", reason);
});

process.on("uncaughtException", (error) => {
  console.error("❌ Uncaught Exception:", error);
});

const server = app.listen(PORT, () => {
  console.log(`✅ Backend running on port ${PORT}`);
  console.log(`🔗 Server is ready to accept requests`);
});

// Keep the server running
server.on("error", (err) => {
  console.error("Server error:", err);
});

process.stdin.resume();
