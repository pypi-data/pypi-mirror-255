import warnings
from typing import Any, Optional

from ...types import (
    FeaturesState, ChatData, CallbackHandler, CompletionData
)


class LunaryCallbackHandler(CallbackHandler):
    """Callback Handler for Lunary`.

    #### Example:
    ```python
    from langchain.llms import OpenAI
    from langchain.callbacks import LunaryCallbackHandler

    lunary_callback = LunaryCallbackHandler()
    llm = OpenAI(callbacks=[lunary_callback],
                 metadata={"userId": "user-123"})
    llm.predict("Hello, how are you?")
    ```
    """

    def __init__(
        self,
        features_state: Optional[FeaturesState] = None,
        **kwargs: Any,
    ) -> None:

        if features_state is None:
            features_state = FeaturesState.only(
                {"on_chat_start": True, "on_chat_end": True, "on_llm_start": True, "on_llm_end": True})
        super().__init__(features_state)

        try:
            import lunary

        except ImportError:
            warnings.warn(
                """[Lunary] To use the Lunary callback handler you need to 
                have the `lunary` Python package installed. Please install it 
                with `pip install lunary`"""
            )

    def on_llm_start(
        self,
        data: CompletionData,
        **kwargs: Any,
    ) -> None:
        try:
            import lunary

            run_id = data.metadata.get("run_id")
            user_id = data.metadata.get("user_id")
            name = data.provider_model

            lunary.track_event(
                run_type="llm",
                event_name="start",
                run_id=run_id,
                name=name,
                user_id=user_id,
                input=[data.prompt.model_dump()],
                output={"response": [out.model_dump()
                                     for out in data.response or []]},
                tags=data.metadata.get("tags"),
            )

        except Exception as e:
            warnings.warn(
                f"[Lunary] An error occurred in on_llm_start: {e}")

    def on_chat_start(
        self,
        data: ChatData,
        **kwargs: Any,
    ) -> Any:
        try:
            import lunary

            run_id = data.metadata.get("run_id")
            user_id = data.metadata.get("user_id")
            name = data.provider_model

            lunary.track_event(
                run_type="llm",
                event_name="start",
                run_id=run_id,
                user_id=user_id,
                name=name,
                input=[message.to_message_dict()
                       for message in data.messages],
                tags=data.metadata.get("tags"),
            )

        except Exception as e:
            warnings.warn(
                f"[Lunary] An error occurred in on_llm_start: {e}")

    def on_chat_end(
        self,
        data: ChatData,
        **kwargs: Any,
    ) -> None:
        try:
            import lunary

            run_id = data.metadata.get("run_id")
            user_id = data.metadata.get("user_id")
            token_usage = data.usage
            name = data.provider_model
            parsed_output = [
                {
                    "text": generation.message.content,
                    "role": "ai",
                    **(
                        {
                            "functionCall": generation.message.function_call.model_dump()
                        }
                        if generation.message.function_call is not None else {}
                    ),
                }
                for generation in data.response or []
            ]

            lunary.track_event(
                run_type="llm",
                event_name="end",
                run_id=run_id,
                user_id=user_id,
                name=name,
                output=parsed_output,
                tags=data.metadata.get("tags"),
                token_usage={
                    "prompt": token_usage.prompt_tokens,
                    "completion": token_usage.completion_tokens,
                } if token_usage is not None else {},
            )

        except Exception as e:
            warnings.warn(f"[Lunary] An error occurred in on_chat_end: {e}")

    def on_llm_end(
        self,
        data: CompletionData,
        **kwargs: Any,
    ) -> None:
        try:
            import lunary

            user_id = data.metadata.get("user_id")
            run_id = data.metadata.get("run_id")
            token_usage = data.usage
            name = data.provider_model
            parsed_output = [
                {
                    "text": generation.text,
                    "role": "ai",
                }
                for generation in data.response or []
            ]

            lunary.track_event(
                run_type="llm",
                event_name="end",
                run_id=run_id,
                user_id=user_id,
                name=name,
                output=parsed_output,
                tags=data.metadata.get("tags"),
                token_usage={
                    "prompt": token_usage.prompt_tokens,
                    "completion": token_usage.completion_tokens,
                } if token_usage is not None else {},
            )

        except Exception as e:
            warnings.warn(f"[Lunary] An error occurred in on_llm_end: {e}")

    # def on_tool_start(
    #     self,
    #     serialized: Dict[str, Any],
    #     input_str: str,
    #     *,
    #     run_id: UUID,
    #     parent_run_id: Union[UUID, None] = None,
    #     tags: Union[List[str], None] = None,
    #     metadata: Union[Dict[str, Any], None] = None,
    #     **kwargs: Any,
    # ) -> None:
    #     if self.__has_valid_config is False:
    #         return
    #     try:
    #         user_id = _get_user_id(metadata)
    #         user_props = _get_user_props(metadata)
    #         name = serialized.get("name")

    #         self.__track_event(
    #             "tool",
    #             "start",
    #             user_id=user_id,
    #             run_id=str(run_id),
    #             parent_run_id=str(parent_run_id) if parent_run_id else None,
    #             name=name,
    #             input=input_str,
    #             tags=tags,
    #             metadata=metadata,
    #             user_props=user_props,
    #         )
    #     except Exception as e:
    #         warnings.warn(
    #             f"[Lunary] An error occurred in on_tool_start: {e}")

    # def on_tool_end(
    #     self,
    #     output: str,
    #     *,
    #     run_id: UUID,
    #     parent_run_id: Union[UUID, None] = None,
    #     tags: Union[List[str], None] = None,
    #     **kwargs: Any,
    # ) -> None:
    #     if self.__has_valid_config is False:
    #         return
    #     try:
    #         self.__track_event(
    #             "tool",
    #             "end",
    #             run_id=str(run_id),
    #             parent_run_id=str(parent_run_id) if parent_run_id else None,
    #             output=output,
    #         )
    #     except Exception as e:
    #         warnings.warn(f"[Lunary] An error occurred in on_tool_end: {e}")
