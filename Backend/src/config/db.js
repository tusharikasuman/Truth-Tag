import mongoose from "mongoose";
import dotenv from "dotenv";

dotenv.config();

const MONGO_URI =
  process.env.MONGO_URI || "mongodb://localhost:27017/truthtag";

export const connectDB = async () => {
  try {
    console.log("🔍 Connecting to MongoDB...");
    console.log("🔗 URI:", MONGO_URI.substring(0, 30) + "...");
    await mongoose.connect(MONGO_URI);
    console.log("✅ MongoDB connected successfully");
  } catch (err) {
    console.error("❌ MongoDB connection error:", err.message);
    process.exit(1);
  }
};

export const disconnectDB = async () => {
  try {
    await mongoose.disconnect();
    console.log("✅ MongoDB disconnected");
  } catch (err) {
    console.error("❌ MongoDB disconnect error:", err);
  }
};
