import warnings
from enum import Enum
from typing import Any, Dict, Optional


from ...types import (
    FeaturesState, ChatData, ManipulationHandler, CompletionData,
    ManipulationHandler, ChatChoices, ChatContent, CompletionChoices
)
from ...utils import CharacterTextSplitter


class CacheType(Enum):
    EXACT = 'exact'
    SIMILAR = 'similar'


class CacheManipulationHandler(ManipulationHandler):
    """Manipulation Handler for Prompts`.

    #### Example:
    ```python
    ```
    """

    def __init__(
        self,
        cache_type: CacheType = CacheType.EXACT,
        features_state: Optional[FeaturesState] = None,
        metadata: Dict[str, Any] = {},
        **kwargs: Any,
    ) -> None:

        if features_state is None:
            features_state = FeaturesState.only(
                {"on_chat_start": True, "on_llm_start": True, "on_llm_end": True, "on_chat_end": True})
        super().__init__(features_state)

        try:
            from gptcache import Cache
            from gptcache.embedding import Onnx
            from gptcache.manager import CacheBase, VectorBase, get_data_manager
            from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
            from gptcache.similarity_evaluation.exact_match import ExactMatchEvaluation
            from gptcache.processor.pre import get_prompt

            print("Cache loading.....")

            self.input_summarizer = None
            self.onnx = Onnx()
            self.data_manager = get_data_manager(
                CacheBase("sqlite"), VectorBase("faiss", dimension=self.onnx.dimension))
            self.cache = Cache()
            self.cache.init(
                pre_embedding_func=get_prompt,
                embedding_func=self.onnx.to_embeddings,
                data_manager=self.data_manager,
                similarity_evaluation=ExactMatchEvaluation(
                ) if cache_type == CacheType.EXACT else SearchDistanceEvaluation(),
            )

        except ImportError:
            warnings.warn(
                "Could not import gptcache python package. "
                "Please install it with `pip install gptcache`."
            )

        self.metadata = metadata

    def on_llm_start(
        self,
        data: CompletionData,
        **kwargs: Any,
    ):
        try:

            from gptcache.adapter.api import get

            data.metadata["summarize_input"] = self.summarize_input(
                data.prompt.content)
            res = get(data.metadata["summarize_input"], cache_obj=self.cache)
            if res:
                data.response = [
                    CompletionChoices(
                        finish_reason="stop",
                        index=0,
                        text=res
                    )
                ]

            return data
        except Exception as e:
            warnings.warn(
                f"[Cache] An error occurred in on_llm_start: {e}")
            return data

    def on_llm_end(
        self,
        data: CompletionData,
        **kwargs: Any,
    ):
        try:

            if data.metadata.get("caching") == True:
                return data

            from gptcache.adapter.api import put

            handled_data = [m.text for m in data.response or []]
            put(data.metadata["summarize_input"],
                handled_data, cache_obj=self.cache)

            return data
        except Exception as e:
            warnings.warn(
                f"[Cache] An error occurred in on_llm_start: {e}")
            return data

    def on_chat_start(
        self,
        data: ChatData,
        **kwargs: Any,
    ):
        try:
            from gptcache.adapter.api import get

            data.metadata["summarize_input"] = self.summarize_input(
                "".join([m.content for m in data.messages]))
            res = get(data.metadata["summarize_input"], cache_obj=self.cache)
            if res:
                data.response = [
                    ChatChoices(
                        finish_reason="stop",
                        index=0,
                        message=ChatContent(content=res)
                    ) if isinstance(res, str) else res
                ]
            return data
        except Exception as e:
            warnings.warn(
                f"[Cache] An error occurred in on_llm_start: {e}")
            return data

    def on_chat_end(
        self,
        data: ChatData,
        **kwargs: Any,
    ):
        try:

            if data.metadata.get("caching") == True:
                return data

            from gptcache.adapter.api import put

            handled_data = [m.message.content for m in data.response or []]
            put(data.metadata["summarize_input"],
                handled_data, cache_obj=self.cache)

            return data
        except Exception as e:
            warnings.warn(
                f"[Cache] An error occurred in on_llm_start: {e}")
            return data

    def truncate_text_tokens(self, text: str):
        splitter = CharacterTextSplitter(is_separator_regex=True)
        return splitter.split_text(text)

    def summarize_input(self, text: str, text_length: int = 512):
        if len(text) <= text_length:
            return text

        from gptcache.processor.context.summarization_context import (
            SummarizationContextProcess,
        )

        if self.input_summarizer is None:
            self.input_summarizer = SummarizationContextProcess(
                model_name="Falconsai/text_summarization")
        summarization = self.input_summarizer.summarize_to_sentence(
            [text], text_length)
        return summarization
