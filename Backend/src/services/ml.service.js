import axios from "axios";
import FormData from "form-data";

export const analyzeFile = async (buffer) => {
  const form = new FormData();
  form.append("file", buffer, "file.jpg");

  const res = await axios.post(
    "http://127.0.0.1:8000/analyze",
    form,
    { headers: form.getHeaders() }
  );

  return res.data;
};
