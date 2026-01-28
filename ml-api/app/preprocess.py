import cv2
import numpy as np

def preprocess_image(image_bytes):
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image")

    img = cv2.resize(img, (299, 299))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    return img
