import tensorflow as tf

model = tf.keras.models.load_model(
    "models/xception_deepfake.h5",
    compile=False
)

def predict(image_tensor):
    pred = model.predict(image_tensor)[0][0]
    return {
        "aiGenerated": bool(pred > 0.5),
        "score": round(float(pred), 2),
        "model": "XceptionNet"
    }
