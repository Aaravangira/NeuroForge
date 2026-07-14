import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL = "/Users/aaravsharma/Qwen2.5-3B-Instruct"

device = "mps" if torch.backends.mps.is_available() else "cpu"

print("Device:", device)

tokenizer = AutoTokenizer.from_pretrained(MODEL)

model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    torch_dtype=torch.bfloat16,
)

model = model.to(device)

prompt = "What is the capital of India?"

inputs = tokenizer(prompt, return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items()}

with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=False
    )

print(tokenizer.decode(output[0], skip_special_tokens=True))