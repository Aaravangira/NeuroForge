from preprocess import ImagePreprocessor
import cv2

processor = ImagePreprocessor()

img = processor.preprocess(
    "output/Prachar 082983_page_1.png"
)

cv2.imwrite(
    "output/preprocessed.png",
    img
)

print("Done")