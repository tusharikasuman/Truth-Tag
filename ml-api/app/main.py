from fastapi import FastAPI, UploadFile, File
from .preprocess import preprocess_image
from .model import predict

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image_tensor = preprocess_image(image_bytes)
    result = predict(image_tensor)
    return result
