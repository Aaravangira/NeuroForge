"""
Image Preprocessing for OCR
"""

import cv2
import numpy as np


class ImagePreprocessor:

    def preprocess(self, image_path):

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Remove noise
        gray = cv2.fastNlMeansDenoising(gray)

        # Improve contrast
        gray = cv2.equalizeHist(gray)

        # Adaptive Threshold
        processed = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11
        )

        return processed