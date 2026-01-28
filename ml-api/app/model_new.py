import numpy as np
import cv2

try:
    import tensorflow as tf
    from keras.applications import EfficientNetB0
    TF_AVAILABLE = True
except ImportError:
    print("⚠️ TensorFlow not available, using basic detection only")
    TF_AVAILABLE = False

# Load pre-trained model for image classification
model = None

def load_model():
    """Load the pre-trained model for AI detection"""
    global model
    if not TF_AVAILABLE:
        print("⚠️ TensorFlow not available, skipping model load")
        return None
        
    if model is None:
        try:
            model = EfficientNetB0(weights='imagenet')
            print("✅ ML Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            model = None
    return model

def preprocess_image(content):
    """Convert bytes to image and preprocess"""
    try:
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None
            
        img = cv2.resize(img, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img, axis=0)
        
        return img
    except Exception as e:
        print(f"❌ Error preprocessing image: {e}")
        return None

def predict(content, filename=""):
    """Analyze file and detect if AI-generated"""
    
    if not content:
        return {"aiGenerated": False, "score": 0.0}
    
    try:
        # Method 1: Metadata analysis
        ai_indicators = detect_metadata_patterns(content, filename)
        
        # Method 2: Image processing
        img = preprocess_image(content)
        if img is not None:
            freq_score = analyze_frequency_domain(img)
            
            # Method 3: Deep learning
            if TF_AVAILABLE:
                model_obj = load_model()
                if model_obj is not None:
                    try:
                        predictions = model_obj.predict(img, verbose=0)
                        max_confidence = np.max(predictions)
                        dl_score = max_confidence * 0.5
                    except Exception as e:
                        print(f"⚠️ DL prediction error: {e}")
                        dl_score = 0.0
                else:
                    dl_score = 0.0
            else:
                dl_score = 0.0
            
            combined_score = (ai_indicators + freq_score + dl_score) / 3
        else:
            combined_score = ai_indicators
        
        is_ai_generated = combined_score > 0.5
        
        return {
            "aiGenerated": is_ai_generated,
            "score": round(combined_score, 2)
        }
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return {"aiGenerated": False, "score": 0.0}

def detect_metadata_patterns(content, filename):
    """Analyze file metadata for AI generation patterns"""
    score = 0.0
    
    try:
        file_size = len(content)
        
        if file_size > 1000000:
            score += 0.1
        elif file_size < 50000:
            score += 0.15
        
        if filename:
            filename_lower = filename.lower()
            ai_keywords = ['ai', 'generated', 'synthetic', 'fake', 'deepfake']
            for keyword in ai_keywords:
                if keyword in filename_lower:
                    score += 0.3
        
        return min(score, 1.0)
    except Exception as e:
        print(f"⚠️ Metadata analysis error: {e}")
        return 0.0

def analyze_frequency_domain(img):
    """Analyze frequency domain characteristics"""
    try:
        if len(img.shape) == 4:
            img_gray = np.mean(img[0], axis=2)
        else:
            img_gray = np.mean(img, axis=2)
        
        fft = np.fft.fft2(img_gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        
        low_freq = np.mean(magnitude[90:110, 90:110])
        high_freq = np.mean(magnitude[:50, :50])
        
        if low_freq > 0:
            freq_ratio = high_freq / low_freq
            score = abs(freq_ratio - 0.3) / 0.5
            score = min(score, 1.0)
        else:
            score = 0.0
            
        return score
    except Exception as e:
        print(f"⚠️ Frequency analysis error: {e}")
        return 0.0
