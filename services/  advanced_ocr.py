import os
import cv2
import fitz
import numpy as np

from PIL import Image
from paddleocr import PaddleOCR

from logger import logger
ocr = PaddleOCR(
    use_doc_orientation_classify=True,
    use_doc_unwarping=True,
    use_textline_orientation=True,
    lang="en"
)
def preprocess_image(image_path):

    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.fastNlMeansDenoising(gray)

    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    kernel = np.array([
        [-1,-1,-1],
        [-1, 9,-1],
        [-1,-1,-1]
    ])

    sharp = cv2.filter2D(binary, -1, kernel)

    return sharp
def image_to_text(image_path):

    img = preprocess_image(image_path)

    result = ocr.predict(img)

    text = []

    for page in result:
        for block in page["rec_texts"]:
            text.append(block)

    return "\n".join(text)
