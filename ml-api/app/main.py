from fastapi import FastAPI, File, UploadFile
from .model import predict, load_models

app = FastAPI(title="TruthTag ML API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Load ML models on startup"""
    print("🚀 Starting ML API...")
    load_models()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """Accept image, video, or any file"""
    content = await file.read()
    filename = file.filename
    return predict(content, filename)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TruthTag ML API"}
