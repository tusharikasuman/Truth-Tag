import numpy as np
import cv2
from scipy import fftpack
from scipy.stats import entropy

# TensorFlow / Keras (safe import)
try:
    import tensorflow as tf
    from keras.applications import Xception, EfficientNetB0
    from keras.applications.xception import preprocess_input as xception_preprocess
    from keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
    TF_AVAILABLE = True
except Exception as e:
    print("⚠️ TensorFlow not available:", e)
    TF_AVAILABLE = False
    # Define fallback preprocess_input
    def xception_preprocess(x):
        """Fallback preprocessing when Keras not available"""
        x /= 127.5
        x -= 1.0
        return x
    
    def efficientnet_preprocess(x):
        """Fallback for EfficientNet"""
        x /= 255.0
        return x

MODEL_PATH = "models/xception.h5"
models_ensemble = {}


def load_models():
    """Load ensemble of models for better accuracy"""
    global models_ensemble
    if not TF_AVAILABLE:
        print("⚠️ TensorFlow not available, using fallback")
        return {}

    if len(models_ensemble) > 0:
        return models_ensemble

    try:
        # Xception model
        xception_base = Xception(
            weights='imagenet',
            include_top=False,
            pooling="avg",
            input_shape=(299, 299, 3),
        )
        xception_model = tf.keras.Sequential([
            xception_base,
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1, activation="sigmoid")
        ])
        models_ensemble['xception'] = xception_model
        print("✅ Xception model loaded")

        # EfficientNetB0 model
        efficientnet_base = EfficientNetB0(
            weights='imagenet',
            include_top=False,
            pooling="avg",
            input_shape=(224, 224, 3),
        )
        efficientnet_model = tf.keras.Sequential([
            efficientnet_base,
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1, activation="sigmoid")
        ])
        models_ensemble['efficientnet'] = efficientnet_model
        print("✅ EfficientNetB0 model loaded")

    except Exception as e:
        print(f"❌ Model load error: {e}")

    return models_ensemble


def analyze_frequency_domain(img_array):
    """Analyze frequency domain characteristics for AI detection"""
    try:
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor((img_array * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            gray = (img_array * 255).astype(np.uint8)
        
        # FFT analysis
        fft = fftpack.fft2(gray)
        fft_shift = fftpack.fftshift(fft)
        magnitude_spectrum = np.abs(fft_shift)
        
        # Calculate spectral statistics
        log_magnitude = np.log1p(magnitude_spectrum)
        spectral_entropy = entropy(log_magnitude.flatten())
        
        # AI-generated images often have more uniform frequency distribution
        # Natural images have more concentrated energy at low frequencies
        center_energy = np.sum(magnitude_spectrum[gray.shape[0]//4:3*gray.shape[0]//4, 
                                                    gray.shape[1]//4:3*gray.shape[1]//4])
        total_energy = np.sum(magnitude_spectrum)
        center_ratio = center_energy / (total_energy + 1e-6)
        
        return {
            "spectral_entropy": float(spectral_entropy),
            "center_energy_ratio": float(center_ratio)
        }
    except Exception as e:
        print(f"⚠️ Frequency analysis error: {e}")
        return {"spectral_entropy": 0.5, "center_energy_ratio": 0.5}


def analyze_metadata_artifacts(content: bytes):
    """Detect AI-specific metadata and artifacts"""
    try:
        import piexif
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Check for suspicious metadata
        has_suspicious_exif = False
        try:
            exif_dict = piexif.load(content)
            # AI tools often have missing or suspicious EXIF data
            if not exif_dict.get("0th"):
                has_suspicious_exif = True
        except:
            has_suspicious_exif = True
        
        return 0.3 if has_suspicious_exif else 0.1
    except:
        return 0.0


def preprocess_xception(content: bytes):
    """Preprocess for Xception (299x299)"""
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    
    img = cv2.resize(img, (299, 299))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = xception_preprocess(img.astype("float32"))
    return np.expand_dims(img, axis=0)


def preprocess_efficientnet(content: bytes):
    """Preprocess for EfficientNetB0 (224x224)"""
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    
    img = cv2.resize(img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = efficientnet_preprocess(img.astype("float32"))
    return np.expand_dims(img, axis=0)


def predict(content: bytes, filename=""):
    """Predict if content is AI-generated using ensemble + frequency analysis"""
    models = load_models()
    
    if not models:
        # Fallback when models unavailable
        return {
            "aiGenerated": False,
            "score": 0.45,
            "confidence": "low"
        }

    predictions = []
    
    try:
        # Xception prediction
        xception_img = preprocess_xception(content)
        if xception_img is not None:
            xception_prob = float(models['xception'].predict(xception_img, verbose=0)[0][0])
            predictions.append(xception_prob)
            print(f"🔍 Xception score: {xception_prob:.3f}")
        
        # EfficientNetB0 prediction
        efficientnet_img = preprocess_efficientnet(content)
        if efficientnet_img is not None:
            efficientnet_prob = float(models['efficientnet'].predict(efficientnet_img, verbose=0)[0][0])
            predictions.append(efficientnet_prob)
            print(f"🔍 EfficientNetB0 score: {efficientnet_prob:.3f}")
        
        # Frequency domain analysis
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_normalized = img_rgb.astype('float32') / 255.0
        
        freq_analysis = analyze_frequency_domain(img_normalized)
        spectral_entropy = freq_analysis["spectral_entropy"]
        center_ratio = freq_analysis["center_energy_ratio"]
        
        # AI images tend to have higher spectral entropy and lower center energy ratio
        freq_score = min(1.0, (spectral_entropy / 8.0) * (1 - center_ratio))
        predictions.append(freq_score)
        print(f"🔍 Frequency analysis score: {freq_score:.3f}")
        
        # Metadata analysis
        metadata_score = analyze_metadata_artifacts(content)
        if metadata_score > 0:
            predictions.append(metadata_score)
            print(f"🔍 Metadata suspicion score: {metadata_score:.3f}")
        
        # Ensemble voting with weighted average
        if predictions:
            final_score = np.mean(predictions)
        else:
            final_score = 0.5
        
        # Determine confidence level
        score_std = np.std(predictions) if len(predictions) > 1 else 0
        if score_std < 0.15:
            confidence = "high"
        elif score_std < 0.3:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "aiGenerated": bool(final_score > 0.5),
            "score": round(float(final_score), 3),
            "confidence": confidence,
            "details": {
                "spectralEntropy": round(spectral_entropy, 3),
                "frequencyScore": round(freq_score, 3),
                "modelsAgree": len(set([p > 0.5 for p in predictions])) == 1
            }
        }
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return {
            "aiGenerated": False,
            "score": 0.0,
            "confidence": "low"
        }
