import axios from "axios";
import FormData from "form-data";

export const analyzeFile = async (fileBuffer) => {
  const formData = new FormData();
  formData.append("file", fileBuffer, "upload");

  const res = await axios.post(
    "http://127.0.0.1:8000/analyze",
    formData,
    {
      headers: formData.getHeaders()
    }
  );

  return res.data;
};
