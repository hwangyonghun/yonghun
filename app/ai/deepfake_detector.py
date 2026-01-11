import os
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMG_SIZE = (128, 128)


def safe_import_numpy():
    try:
        import numpy as np
        return np
    except Exception as e:
        logger.error(f"NumPy import failed: {e}")
        return None


def safe_import_pil():
    try:
        from PIL import Image
        return Image
    except Exception as e:
        logger.error(f"PIL import failed: {e}")
        return None


class DeepfakeDetector:
    def __init__(self, model_path="deepfake_model.h5"):
        self.model = None
        self.use_mock = True  # 🔴 mock 기본값
        self.np = safe_import_numpy()
        self.Image = safe_import_pil()

        if self.np is None or self.Image is None:
            logger.warning("Required libraries missing. Using mock mode.")
            return

        self._load_model_safe(model_path)

    def _load_model_safe(self, model_path):
        try:
            import tensorflow as tf
        except Exception as e:
            logger.warning(f"TensorFlow unavailable: {e}")
            return

        if not os.path.exists(model_path):
            logger.warning("Model file not found. Using mock.")
            return

        try:
            self.model = tf.keras.models.load_model(model_path)
            self.use_mock = False
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Model load failed: {e}")

    def preprocess_image(self, image_input):
        if self.Image is None or self.np is None:
            raise RuntimeError("Image processing libraries not available")

        if isinstance(image_input, str):
            img = self.Image.open(image_input).convert("RGB")
        elif isinstance(image_input, self.Image.Image):
            img = image_input.convert("RGB")
        else:
            raise ValueError("image_input must be file path or PIL.Image")

        img = img.resize(IMG_SIZE)
        arr = self.np.array(img, dtype="float32") / 255.0
        return self.np.expand_dims(arr, axis=0)

    def detect_deepfake(self, image_input):
        if not self.use_mock and self.model is not None:
            try:
                processed = self.preprocess_image(image_input)
                prediction = self.model.predict(processed)
                prob = float(self.np.asarray(prediction).squeeze())
                return float(self.np.clip(prob, 0.0, 1.0))
            except Exception as e:
                logger.error(f"Prediction failed: {e}")
                self.use_mock = True

        # ✅ 안전한 mock
        base = self.np.random.rand() if self.np else 0.5
        return 0.8 if base > 0.5 else 0.2