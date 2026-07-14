"""
==========================================
AI ENGINE
AI Invoice Extractor
==========================================
"""

import json
import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)

from logger import logger

from config import (
    MODEL_PATH,
    DEVICE,
    MAX_NEW_TOKENS,
    TEMPERATURE
)

# ==========================================
# PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are an expert Invoice Extraction AI.

Your task is to extract invoice fields ONLY from the provided OCR text.

Rules:

1. Never guess.
2. If a value is not present, return "".
3. Preserve invoice numbers exactly.
4. Preserve GST numbers exactly.
5. Preserve dates exactly as written.
6. Preserve currency exactly.
7. Preserve monetary values exactly.
8. Return ONLY valid JSON.
9. Do not add explanations.
10. Do not use markdown.

JSON Schema:

{
  "vendor_name":"",
  "invoice_number":"",
  "invoice_date":"",
  "gst_number":"",
  "subtotal":"",
  "tax":"",
  "grand_total":"",
  "payment_method":"",
  "currency":""
}
"""

def empty_result():

    return {
        "vendor_name":"",
        "invoice_number":"",
        "invoice_date":"",
        "gst_number":"",
        "subtotal":"",
        "tax":"",
        "grand_total":"",
        "payment_method":"",
        "currency":""
    }
def clean_json(response):

    response = response.strip()

    response = response.replace("```json", "")

    response = response.replace("```", "")

    return response.strip()
# ==========================================
# LOAD MODEL
# ==========================================

logger.info("Loading Qwen Model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    dtype=torch.bfloat16
)

model = model.to(DEVICE)

model.eval()

logger.info("Qwen Model Loaded Successfully")
def extract_document(document_text):

    try:

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": document_text
            }
        ]

        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = tokenizer(
            prompt,
            return_tensors="pt"
        )

        inputs = {
            k: v.to(DEVICE)
            for k, v in inputs.items()
        }

        with torch.no_grad():

            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                do_sample=False
            )

        text = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )

        text = clean_json(text)

        data = json.loads(text)

        result = empty_result()

        result.update(data)

        logger.info("AI Extraction Successful")

        return result

    except Exception as e:

        logger.exception(e)

        return empty_result()