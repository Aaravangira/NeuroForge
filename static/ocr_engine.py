from paddleocr import PaddleOCR
from PIL import Image
import fitz
import os

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="en"
)


def image_to_text(image_path):

    result = ocr.predict(image_path)

    text = ""

    for page in result:

        for line in page["rec_texts"]:

            text += line + "\n"

    return text


def pdf_to_text_with_ocr(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page_number in range(len(doc)):

        page = doc.load_page(page_number)

        pix = page.get_pixmap(dpi=300)

        image_name = f"temp_{page_number}.png"

        pix.save(image_name)

        text += image_to_text(image_name)

        os.remove(image_name)

    doc.close()

    return text