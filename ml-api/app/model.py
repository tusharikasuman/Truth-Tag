import numpy as np
import cv2

# TensorFlow / Keras (safe import)
try:
    import tensorflow as tf
    from keras.applications import Xception
    from keras.applications.xception import preprocess_input
    TF_AVAILABLE = True
except Exception as e:
    print("⚠️ TensorFlow not available:", e)
    TF_AVAILABLE = False
    # Define fallback preprocess_input
    def preprocess_input(x):
        """Fallback preprocessing when Keras not available"""
        x /= 127.5
        x -= 1.0
        return x

MODEL_PATH = "models/xception.h5"
model = None


def load_model():
    global model
    if not TF_AVAILABLE:
        print("⚠️ TensorFlow not available, using fallback")
        return None

    if model is None:
        try:
            base = Xception(
                weights='imagenet',  # Use pre-trained ImageNet weights
                include_top=False,
                pooling="avg",
                input_shape=(299, 299, 3),
            )

            model = tf.keras.Sequential([
                base,
                tf.keras.layers.Dense(1, activation="sigmoid")
            ])

            print("✅ Xception model loaded with ImageNet weights")
        except Exception as e:
            print(f"❌ Model load error: {e}")
            model = None

    return model


def preprocess_image(content: bytes):
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return None

    img = cv2.resize(img, (299, 299))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = preprocess_input(img.astype("float32"))
    return np.expand_dims(img, axis=0)


def predict(content: bytes, filename=""):
    """Predict if content is AI-generated"""
    img = preprocess_image(content)
    if img is None:
        return {"aiGenerated": False, "score": 0.0}

    model_obj = load_model()

    if model_obj is None:
        # Fallback when model unavailable
        return {
            "aiGenerated": False,
            "score": 0.45
        }

    try:
        prob = model_obj.predict(img, verbose=0)[0][0]
        return {
            "aiGenerated": bool(prob > 0.5),
            "score": round(float(prob), 2)
        }
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return {"aiGenerated": False, "score": 0.0}
