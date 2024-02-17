import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiohttp
import numpy as np
import requests

from ..types import (
    CallbackManager, Callbacks, EmbeddingsData,
    ProviderBase, ManipulationManager,
    Manipulations, GradientInput, embeddings_decorator,
    create_base_retry_decorator
)


class GradientProvider(ProviderBase):

    def __init__(self, configs: GradientInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)

    @classmethod
    def model_validate(cls, configs: GradientInput):
        cls.client = TinyAsyncGradientEmbeddingClient(
            access_token=configs.api_key,
            workspace_id=configs.workspace_id
        )

    @embeddings_decorator
    def embedding(
        self,
        texts: List[str],
        data: Optional[EmbeddingsData],
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
            documents_embeddings = self.client.embed(
                model=self.configs.provider_model, texts=data.embeddings_inputs)
            data.response = documents_embeddings

            return data
        except Exception as e:
            raise e


class TinyAsyncGradientEmbeddingClient:

    def __init__(
        self,
        access_token: Optional[str] = None,
        workspace_id: Optional[str] = None,
        host: str = "https://api.gradient.ai/api",
        aiosession: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self.access_token = access_token or os.environ.get(
            "GRADIENT_ACCESS_TOKEN", None
        )
        self.workspace_id = workspace_id or os.environ.get(
            "GRADIENT_WORKSPACE_ID", None
        )
        self.host = host
        self.aiosession = aiosession

        if self.access_token is None or len(self.access_token) < 10:
            raise ValueError(
                "env variable `GRADIENT_ACCESS_TOKEN` or "
                " param `access_token` must be set "
            )

        if self.workspace_id is None or len(self.workspace_id) < 3:
            raise ValueError(
                "env variable `GRADIENT_WORKSPACE_ID` or "
                " param `workspace_id` must be set"
            )

        if self.host is None or len(self.host) < 3:
            raise ValueError(" param `host` must be set to a valid url")
        self._batch_size = 128

    @staticmethod
    def _permute(
        texts: List[str], sorter: Callable = len
    ) -> Tuple[List[str], Callable]:

        if len(texts) == 1:
            # special case query
            return texts, lambda t: t
        length_sorted_idx = np.argsort([-sorter(sen) for sen in texts])
        texts_sorted = [texts[idx] for idx in length_sorted_idx]

        return texts_sorted, lambda unsorted_embeddings: [  # noqa E731
            unsorted_embeddings[idx] for idx in np.argsort(length_sorted_idx)
        ]

    def _batch(self, texts: List[str]) -> List[List[str]]:
        """
        splits Lists of text parts into batches of size max `self._batch_size`
        When encoding vector database,

        Args:
            texts (List[str]): List of sentences
            self._batch_size (int, optional): max batch size of one request.

        Returns:
            List[List[str]]: Batches of List of sentences
        """
        if len(texts) == 1:
            # special case query
            return [texts]
        batches = []
        for start_index in range(0, len(texts), self._batch_size):
            batches.append(texts[start_index : start_index + self._batch_size])
        return batches

    @staticmethod
    def _unbatch(batch_of_texts: List[List[Any]]) -> List[Any]:
        if len(batch_of_texts) == 1 and len(batch_of_texts[0]) == 1:
            # special case query
            return batch_of_texts[0]
        texts = []
        for sublist in batch_of_texts:
            texts.extend(sublist)
        return texts

    def _kwargs_post_request(self, model: str, texts: List[str]) -> Dict[str, Any]:
        """Build the kwargs for the Post request, used by sync

        Args:
            model (str): _description_
            texts (List[str]): _description_

        Returns:
            Dict[str, Collection[str]]: _description_
        """
        return dict(
            url=f"{self.host}/embeddings/{model}",
            headers={
                "authorization": f"Bearer {self.access_token}",
                "x-gradient-workspace-id": f"{self.workspace_id}",
                "accept": "application/json",
                "content-type": "application/json",
            },
            json=dict(
                inputs=[{"input": i} for i in texts],
            ),
        )

    def _sync_request_embed(
        self, model: str, batch_texts: List[str]
    ) -> List[List[float]]:
        response = requests.post(
            **self._kwargs_post_request(model=model, texts=batch_texts)
        )
        if response.status_code != 200:
            raise Exception(
                f"Gradient returned an unexpected response with status "
                f"{response.status_code}: {response.text}"
            )
        return [e["embedding"] for e in response.json()["embeddings"]]

    def embed(self, model: str, texts: List[str]) -> List[List[float]]:
        perm_texts, unpermute_func = self._permute(texts)
        perm_texts_batched = self._batch(perm_texts)

        # Request
        map_args = (
            self._sync_request_embed,
            [model] * len(perm_texts_batched),
            perm_texts_batched,
        )
        if len(perm_texts_batched) == 1:
            embeddings_batch_perm = list(map(*map_args))
        else:
            with ThreadPoolExecutor(32) as p:
                embeddings_batch_perm = list(p.map(*map_args))

        embeddings_perm = self._unbatch(embeddings_batch_perm)
        embeddings = unpermute_func(embeddings_perm)
        return embeddings

    async def _async_request(
        self, session: aiohttp.ClientSession, kwargs: Dict[str, Any]
    ) -> List[List[float]]:
        async with session.post(**kwargs) as response:
            if response.status != 200:
                raise Exception(
                    f"Gradient returned an unexpected response with status "
                    f"{response.status}: {response.text}"
                )
            embedding = (await response.json())["embeddings"]
            return [e["embedding"] for e in embedding]

    async def aembed(self, model: str, texts: List[str]) -> List[List[float]]:
        """call the embedding of model, async method

        Args:
            model (str): to embedding model
            texts (List[str]): List of sentences to embed.

        Returns:
            List[List[float]]: List of vectors for each sentence
        """
        perm_texts, unpermute_func = self._permute(texts)
        perm_texts_batched = self._batch(perm_texts)

        # Request
        if self.aiosession is None:
            self.aiosession = aiohttp.ClientSession(
                trust_env=True, connector=aiohttp.TCPConnector(limit=32)
            )
        async with self.aiosession as session:
            embeddings_batch_perm = await asyncio.gather(
                *[
                    self._async_request(
                        session=session,
                        **self._kwargs_post_request(model=model, texts=t),
                    )
                    for t in perm_texts_batched
                ]
            )

        embeddings_perm = self._unbatch(embeddings_batch_perm)
        embeddings = unpermute_func(embeddings_perm)
        return embeddings
