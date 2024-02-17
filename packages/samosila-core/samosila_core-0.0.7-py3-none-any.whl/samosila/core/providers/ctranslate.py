from typing import List

from ..types import (
    CallbackManager, ProviderBase, ManipulationManager,
    CTranslateInput,
)


class CTranslateProvider(ProviderBase):

    def __init__(self, configs: CTranslateInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: CTranslateInput = configs

    @classmethod
    def model_validate(cls, configs: CTranslateInput):
        try:
            import ctranslate2
            import huggingface_hub
            import transformers
        except ImportError as e:
            raise ImportError(
                "Could not import ctranslate2 or transformers or huggingface_hub python package. "
                "Please install it with `pip install ctranslate2 huggingface_hub transformers`."
            ) from e
        from ctranslate2 import Translator
        from huggingface_hub import snapshot_download
        from transformers.models.nllb.tokenization_nllb_fast import NllbTokenizerFast

        cls.model_path = snapshot_download(
            'winstxnhdw/nllb-200-distilled-1.3B-ct2-int8')

        cls.translator = Translator(
            cls.model_path, device=configs.device, compute_type='auto')
        cls.tokeniser = NllbTokenizerFast.from_pretrained(
            cls.model_path, local_files_only=True)

    def translate(self, texts: List[str], src_lang: str, des_lang: str = "eng_Latn", callbacks=None):
        try:
            self.tokeniser.src_lang = src_lang

            outputs = texts
            for i, text in enumerate(texts):
                outputs[i] = ""
                lines = [line for line in text.splitlines() if line]

                generator = (
                    f'{self.tokeniser.decode(self.tokeniser.convert_tokens_to_ids(result.hypotheses[0][1:]))}\n'
                    for result in self.translator.translate_iterable(
                        (self.tokeniser(line).tokens() for line in lines),
                        ([des_lang] for _ in lines),
                        beam_size=1
                    )
                )
                for translation in generator:
                    outputs[i] += translation

            return outputs

        except Exception as e:
            raise e
