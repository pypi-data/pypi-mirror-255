from __future__ import annotations

import datetime
from typing import Any, Callable, Dict, List, Optional

from ...types import (
    FeaturesState, ChatData, CallbackHandler, CompletionData
)


def _lazy_import_promptlayer():
    try:
        import promptlayer
    except ImportError:
        raise ImportError(
            "The PromptLayerCallbackHandler requires the promptlayer package. "
            " Please install it with `pip install promptlayer`."
        )
    return promptlayer


class PromptLayerCallbackHandler(CallbackHandler):
    """Callback handler for promptlayer."""

    def __init__(
        self,
        pl_id_callback: Optional[Callable[..., Any]] = None,
        pl_tags: Optional[List[str]] = None,
        features_state: Optional[FeaturesState] = None,
    ) -> None:
        if features_state is None:
            features_state = FeaturesState.only(
                {"on_chat_start": True, "on_chat_end": True, "on_llm_start": True, "on_llm_end": True})
        super().__init__(features_state)

        _lazy_import_promptlayer()

        self.pl_id_callback = pl_id_callback
        self.pl_tags = pl_tags or []
        self.runs: Dict[str, Dict[str, Any]] = {}

    def on_chat_start(
        self,
        data: ChatData,
        **kwargs: Any,
    ) -> Any:
        self.runs[data.metadata.get("run_id") or ""] = {
            "request_start_time": datetime.datetime.now().timestamp(),
        }

    def on_llm_start(
        self,
        data: CompletionData,
        **kwargs: Any,
    ) -> Any:
        self.runs[data.metadata.get("run_id") or ""] = {
            "request_start_time": datetime.datetime.now().timestamp(),
        }

    def on_llm_end(
        self,
        data: CompletionData,
        **kwargs: Any,
    ) -> None:
        from promptlayer.utils import get_api_key, promptlayer_api_request

        run_info = self.runs.get(data.metadata["run_id"], {})
        if not run_info:
            return
        run_info["request_end_time"] = datetime.datetime.now().timestamp()

        pl_request_id = promptlayer_api_request(
            function_name=run_info.get(
                "name") or "openai.Completion.create",
            provider_type="openai",
            args=[],
            kwargs={
                "model": data.provider_model,
                "prompt": data.prompt.content
            },
            tags=self.pl_tags,
            response={
                "choices": [
                    {
                        "finish_reason": generation.finish_reason,
                        "index": generation.index,
                        "logprobs": None,
                        "text": generation.text
                    } for generation in data.response or []
                ],
                "created": data.created,
                "id": data.uuid,
                "model": data.provider_model,
                "object": "chat_completion",
                "usage": {
                    "completion_tokens": data.usage.completion_tokens,
                    "prompt_tokens": data.usage.prompt_tokens,
                    "total_tokens": data.usage.total_tokens
                } if data.usage is not None else {}
            },
            request_start_time=run_info.get("request_start_time"),
            request_end_time=run_info.get("request_end_time"),
            api_key=get_api_key(),
            return_pl_id=bool(self.pl_id_callback is not None),
            metadata={
                "_run_id": str(data.metadata["run_id"]),
                "_openserver_tags": str(data.metadata.get("tags", [])),
            },
        )

        if self.pl_id_callback:
            self.pl_id_callback(pl_request_id)

    def on_chat_end(
        self,
        data: ChatData,
        **kwargs: Any,
    ) -> None:
        from promptlayer.utils import get_api_key, promptlayer_api_request

        run_info = self.runs.get(data.metadata["run_id"], {})
        if not run_info:
            return
        run_info["request_end_time"] = datetime.datetime.now().timestamp()

        pl_request_id = promptlayer_api_request(
            function_name=run_info.get(
                "name") or "openai.ChatCompletion.create",
            provider_type="openai",
            args=[],
            kwargs={
                "model": data.provider_model,
                "messages": [{"content": m.content, "role": m.role} for m in data.messages]
            },
            tags=self.pl_tags,
            response={
                "choices": [
                    {
                        "finish_reason": generation.finish_reason,
                        "index": generation.index,
                        "logprobs": None,
                        "message": generation.message.to_message_dict()
                    } for generation in data.response or []
                ],
                "created": data.created,
                "id": data.uuid,
                "model": data.provider_model,
                "object": "chat_completion",
                "usage": {
                    "completion_tokens": data.usage.completion_tokens,
                    "prompt_tokens": data.usage.prompt_tokens,
                    "total_tokens": data.usage.total_tokens
                } if data.usage is not None else {}
            },
            request_start_time=run_info.get("request_start_time"),
            request_end_time=run_info.get("request_end_time"),
            api_key=get_api_key(),
            return_pl_id=bool(self.pl_id_callback is not None),
            metadata={
                "_run_id": str(data.metadata["run_id"]),
                "_openserver_tags": str(data.metadata.get("tags", [])),
            },
        )

        if self.pl_id_callback:
            self.pl_id_callback(pl_request_id)
