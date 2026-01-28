import express from "express";
import cors from "cors";
import verifyRoute from "./routes/verify.js";

const app = express();
app.use(cors());
app.use(express.json());

app.use("/verify", verifyRoute);

app.listen(5000, () => {
  console.log("Backend running on port 5000");
});
