import time
import torch
import accelerate
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer, BitsAndBytesConfig, AutoTokenizer

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = M2M100ForConditionalGeneration.from_pretrained(
    "facebook/m2m100_418M",)
device = torch.device("cuda:0")
tokenizer = M2M100Tokenizer.from_pretrained(
    "facebook/m2m100_418M",    
    device=device
    
)


def translate_text(text: str, src_lang: str, tgt_lang: str):

    tokenizer.src_lang = src_lang
    encoded_text = tokenizer(text, return_tensors="pt")
    translated_text = ''

    if tgt_lang == "fr":
        forced_bos_token_id = tokenizer.get_lang_id("fr")
        generated_tokens = model.generate(
            **encoded_text, forced_bos_token_id=forced_bos_token_id)
        translated_text = tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True)[0]

    elif tgt_lang == "en":
        forced_bos_token_id = tokenizer.get_lang_id("en")
        generated_tokens = model.generate(
            **encoded_text, forced_bos_token_id=forced_bos_token_id)
        translated_text = tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True)[0]

    elif tgt_lang == "fa":
        forced_bos_token_id = tokenizer.get_lang_id("fa")
        generated_tokens = model.generate(
            **encoded_text, forced_bos_token_id=forced_bos_token_id)
        translated_text = tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True)[0]

    return translated_text


start = time.time()
res = translate_text("سلام", "fa", "en")
print(time.time() - start)
print(res)

start = time.time()
res = translate_text(
    "آیا VAR کمکی به کاهش اشتباهات داوری در دربی کرد؟", "fa", "en")
print(time.time() - start)
print(res)
