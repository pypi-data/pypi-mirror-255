from typing import Any, Dict, List, Optional, Union

from ..utils.image import load_image
from ..types import (
    CallbackManager, Callbacks, ChatMessages, completion_decorator,
    ProviderBase, Message, ManipulationManager,
    Manipulations, HuggingFaceInput, completion_decorator,
    CompletionData, create_base_retry_decorator, ChatData,
    EmbeddingsData, chat_decorator, embeddings_decorator
)


class HuggingFaceProvider(ProviderBase):

    def __init__(self, configs: HuggingFaceInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: HuggingFaceInput = configs
        self.sentence_name = self.configs.provider_model
        self.sentence_client = None

    @classmethod
    def model_validate(cls, configs: HuggingFaceInput):
        try:
            import torch
            import transformers
            import sentence_transformers
        except ImportError as e:
            raise ImportError(
                "Could not import torch or transformers or sentence_transformers python package. "
                "Please install it with `pip install torch transformers sentence_transformers`."
                "Note 📝 : For GPU Acceleration please install cuda if available for torch with `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`"
            ) from e

    @completion_decorator
    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[HuggingFaceInput] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> CompletionData:
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.chat_with_retry(data, callbacks)
            return data
        except Exception as e:
            raise e

    @chat_decorator
    def chat(
        self,
        messages: ChatMessages,
        data: Optional[ChatData] = None,
        configs: Optional[HuggingFaceInput] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> ChatData:
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.chat_with_retry(data, callbacks)
            return data
        except Exception as e:
            raise e

    def chat_with_retry(self, data: Union[CompletionData, ChatData], callbacks) -> Any:

        retry_decorator = create_base_retry_decorator(
            [], max_retries=self.configs.max_retries, run_manager=self.callback_manager)

        @retry_decorator
        def _chat_with_retry(data: Union[CompletionData, ChatData], callbacks) -> Any:
            return self.generate_text(data, callbacks)

        return _chat_with_retry(data, callbacks)

    def generate_text(self, data: Union[CompletionData, ChatData], callbacks):
        try:
            return data
        except Exception as e:
            raise e

    @embeddings_decorator
    def embedding(
        self,
        texts: List[str],
        data: Optional[EmbeddingsData],
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        try:
            data = self.embed_with_retry(data, callbacks)
            return data
        except Exception as e:
            raise e

    def embed_with_retry(self, data: EmbeddingsData, callbacks):

        retry_decorator = create_base_retry_decorator(
            [], max_retries=self.configs.max_retries, run_manager=self.callback_manager)

        @retry_decorator
        def _chat_with_retry(data: EmbeddingsData, callbacks):
            return self.embeddings(data, callbacks)

        return _chat_with_retry(data, callbacks)

    def embeddings(self, data: EmbeddingsData, callbacks):
        try:

            import sentence_transformers

            if self.sentence_client is None or self.sentence_name is not self.configs.provider_model:
                self.sentence_client = sentence_transformers.SentenceTransformer(
                    self.configs.provider_model,
                    cache_folder=self.configs.cache_folder,
                    device=self.configs.device
                )
                self.sentence_name = self.configs.provider_model
            client = self.sentence_client

            texts = list(map(lambda x: x.replace(
                "\n", " "), data.embeddings_inputs))
            if self.configs.multi_process:
                pool = client.start_multi_process_pool()
                embeddings = client.encode_multi_process(texts, pool)
                sentence_transformers.SentenceTransformer.stop_multi_process_pool(
                    pool)
            else:
                embeddings = client.encode(texts)

            _data = embeddings.tolist()

            data.response = _data

            return data
        except Exception as e:
            raise e

    def image_search(self, img_paths: List[str], text: str, multilingual: bool = False, callbacks=None):
        try:
            import torch
            from sentence_transformers import SentenceTransformer, util

            img_model = SentenceTransformer('clip-ViT-B-32')
            text_model = img_model if multilingual == False else SentenceTransformer(
                'sentence-transformers/clip-ViT-B-32-multilingual-v1')

            images = [load_image(img) for img in img_paths]

            img_embeddings = img_model.encode(images)
            text_embedding = text_model.encode(text)

            cos_sim = util.cos_sim(text_embedding, img_embeddings)
            max_img_idx = torch.argmax(cos_sim)

            return text, cos_sim[max_img_idx], img_paths[max_img_idx]
        except Exception as e:
            raise e

    def translate(self, texts: List[str], src_lang: str, des_lang: str = "en", callbacks=None):
        try:

            import torch
            from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

            model = M2M100ForConditionalGeneration.from_pretrained(
                "facebook/m2m100_418M",
                dtype=torch.float16,
            )
            device = torch.device("cuda")
            tokenizer = M2M100Tokenizer.from_pretrained(
                "facebook/m2m100_418M",
                device=device
            )

            tokenizer.src_lang = src_lang
            forced_bos_token_id = tokenizer.get_lang_id(des_lang)
            translated_texts = []

            for text in texts:

                encoded_text = tokenizer(text, return_tensors="pt")
                generated_tokens = model.generate(
                    **encoded_text, forced_bos_token_id=forced_bos_token_id)
                translated_text = tokenizer.batch_decode(
                    generated_tokens, skip_special_tokens=True)[0]
                translated_texts.append(translated_text)

            return translated_texts

        except Exception as e:
            raise e

    def summarize_to_sentence(self, sentences: List[str], target_length=512, tokenizer="roberta-base", callbacks=None):
        try:
            import transformers
            import numpy as np

            summarizer = transformers.pipeline(
                task="summarization", model=self.configs.provider_model)
            tokenizer = transformers.RobertaTokenizer.from_pretrained(
                tokenizer)

            lengths = []
            for sentence in sentences:
                lengths.append(len(sentence))
            total_length = np.array(lengths).sum()
            target_lengths = [int(target_length * l / total_length)
                              for l in lengths]

            result = ""
            for sent, target_len in zip(sentences, target_lengths):
                if len(tokenizer.tokenize(sent)) > target_len:
                    response = summarize_to_length(
                        summarizer, sent, target_len, tokenizer.model_max_length
                    )
                    target_sentence = response
                else:
                    target_sentence = sent
                result = result + target_sentence

            return result

        except Exception as e:
            raise e


def summarize_to_length(summarizer, text: str, target_len, max_len=1024):
    tokenizer = summarizer.tokenizer

    def token_length(text):
        return len(tokenizer.encode(text))

    segment_len = max_len - 100
    summary_result = text
    while token_length(text) > target_len:
        tokens = tokenizer.encode(text)
        segments = [
            tokens[i: i + segment_len] for i in range(0, len(tokens), segment_len - 1)
        ]
        summary_result = ""
        for segment in segments:
            len_seg = int(len(segment) / 4)
            summary = summarizer(
                tokenizer.decode(segment),
                min_length=max(len_seg - 10, 1),
                max_length=len_seg,
            )
            summary_result += summary[0]["summary_text"]
        text = summary_result
    return summary_result


# text_to_speach
# transcription
# generate_text
# chat
