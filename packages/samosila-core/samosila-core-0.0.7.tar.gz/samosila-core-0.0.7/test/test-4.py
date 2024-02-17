from time import time
from typing import Generator

from ctranslate2 import Translator as CTranslator
from huggingface_hub import snapshot_download
from transformers.models.nllb.tokenization_nllb_fast import NllbTokenizerFast

class Translator:
    tokeniser: NllbTokenizerFast
    translator: CTranslator

    @classmethod
    def load(cls):
        model_path = snapshot_download(
            'winstxnhdw/nllb-200-distilled-1.3B-ct2-int8')
        device = 'cpu'

        cls.translator = CTranslator(
            model_path, device=device, compute_type='auto')
        cls.tokeniser = NllbTokenizerFast.from_pretrained(
            model_path, local_files_only=True)

    @classmethod
    def translate(cls, text: str, source_language: str, target_language: str) -> Generator[str, None, None]:
        cls.tokeniser.src_lang = source_language

        lines = [line for line in text.splitlines() if line]

        return (
            f'{cls.tokeniser.decode(cls.tokeniser.convert_tokens_to_ids(result.hypotheses[0][1:]))}\n'
            for result in cls.translator.translate_iterable(
                (cls.tokeniser(line).tokens() for line in lines),
                ([target_language] for _ in lines),
                beam_size=1
            )
        )


translator = Translator()


start = time()
Translator.load()
print(f"start time : {time() - start}")

batched_input = [
    'We now have 4-month-old mice that are non-diabetic that used to be diabetic," he added.',
    "Dr. Ehud Ur, professor of medicine at Dalhousie University in Halifax, Nova Scotia and chair of the clinical and scientific division of the Canadian Diabetes Association cautioned that the research is still in its early days."
    "Like some other experts, he is skeptical about whether diabetes can be cured, noting that these findings have no relevance to people who already have Type 1 diabetes."
    "On Monday, Sara Danius, permanent secretary of the Nobel Committee for Literature at the Swedish Academy, publicly announced during a radio program on Sveriges Radio in Sweden the committee, unable to reach Bob Dylan directly about winning the 2016 Nobel Prize in Literature, had abandoned its efforts to reach him.",
    'Danius said, "Right now we are doing nothing. I have called and sent emails to his closest collaborator and received very friendly replies. For now, that is certainly enough."',
    "Previously, Ring's CEO, Jamie Siminoff, remarked the company started when his doorbell wasn't audible from his shop in his garage.",
]

outputs = []

for inp in batched_input:  
  start = time()
  generator = Translator.translate(inp, "eng_Latn", "pes_Arab")
  for translation in generator:
      outputs.append(translation)
  print(time() - start)


with open("output.txt", "w", encoding="utf-8") as f:
    for string in outputs:
        f.write(string + "\n\n")
