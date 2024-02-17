from typing import Any, Dict, List, Optional

from ..types import (
    CallbackManager, Callbacks, EmbeddingsData,
    ProviderBase, ManipulationManager,
    Manipulations, VoyageInput,
    embeddings_decorator, create_base_retry_decorator
)


class VoyageProvider(ProviderBase):

    def __init__(self, configs: VoyageInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)

    @classmethod
    def model_validate(cls, configs: VoyageInput):
        try:
            import voyageai
        except ImportError as e:
            raise ImportError(
                "Could not import voyage python package. "
                "Please install it with `pip install voyageai`."
            ) from e

    @embeddings_decorator
    def embedding(
        self,
        texts: List[str],
        data: Optional[EmbeddingsData] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> EmbeddingsData:
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.embed_with_retry(data, callbacks)
            return data
        except Exception as e:
            raise e

    def embed_with_retry(self, data: EmbeddingsData, callbacks):

        retry_decorator = create_base_retry_decorator(
            [], max_retries=self.configs.max_retries, run_manager=self.callback_manager)

        @retry_decorator
        def _embed_with_retry(data: EmbeddingsData, callbacks):
            return self.embeddings(data, callbacks)

        return _embed_with_retry(data, callbacks)

    def embeddings(self, data: EmbeddingsData, callbacks):
        try:
            from voyageai import get_embeddings

            documents_embeddings = get_embeddings(
                data.embeddings_inputs, model=self.configs.provider_model, input_type="document")
            data.response = documents_embeddings

            return data
        except Exception as e:
            raise e
