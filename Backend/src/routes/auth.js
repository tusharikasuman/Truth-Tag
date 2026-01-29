import express from "express";
import User from "../models/User.js";
import { generateToken, verifyToken, authMiddleware } from "../services/auth.service.js";

const router = express.Router();

// 📝 Register
router.post("/register", async (req, res) => {
  try {
    const { email, password, name } = req.body;

    if (!email || !password || !name) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    // Check if user exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(409).json({ error: "User already exists" });
    }

    // Create new user
    const user = new User({ email, password, name });
    await user.save();

    const token = generateToken(user._id, user.email);

    res.status(201).json({
      message: "User registered successfully",
      token,
      user: {
        id: user._id,
        email: user.email,
        name: user.name,
      },
    });
  } catch (err) {
    console.error("❌ Register error:", err);
    res.status(500).json({ error: "Registration failed" });
  }
});

// 🔓 Login
router.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: "Email and password required" });
    }

    // Find user
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    // Check password
    const isValid = await user.comparePassword(password);
    if (!isValid) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const token = generateToken(user._id, user.email);

    res.json({
      message: "Login successful",
      token,
      user: {
        id: user._id,
        email: user.email,
        name: user.name,
      },
    });
  } catch (err) {
    console.error("❌ Login error:", err);
    res.status(500).json({ error: "Login failed" });
  }
});

// ✅ Verify token
router.post("/verify", authMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId);
    res.json({
      valid: true,
      user: {
        id: user._id,
        email: user.email,
        name: user.name,
      },
    });
  } catch (err) {
    res.status(500).json({ error: "Verification failed" });
  }
});

// 👤 Get profile
router.get("/profile", authMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId);
    res.json({
      user: {
        id: user._id,
        email: user.email,
        name: user.name,
        verifications: user.verifications,
      },
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch profile" });
  }
});

// 🚪 Logout (frontend handles token removal)
router.post("/logout", authMiddleware, (req, res) => {
  res.json({ message: "Logout successful" });
});

export default router;
