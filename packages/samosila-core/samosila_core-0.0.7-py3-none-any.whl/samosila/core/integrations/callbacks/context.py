import os
from typing import Any, Dict, List, Optional

from ...types import (
    FeaturesState, ChatData, CallbackHandler
)


def import_context() -> Any:
    """Import the `getcontext` package."""
    try:
        import getcontext  # noqa: F401
        from getcontext.generated.models import (
            Conversation,
            Message,
            MessageRole,
            Rating,
        )
        from getcontext.token import Credential  # noqa: F401
    except ImportError:
        raise ImportError(
            "To use the context callback manager you need to have the "
            "`getcontext` python package installed (version >=0.3.0). "
            "Please install it with `pip install --upgrade context-python`"
        )
    return getcontext, Credential, Conversation, Message, MessageRole, Rating


class ContextCallbackHandler(CallbackHandler):
    """Callback Handler that records transcripts to the Context service.

     (https://context.ai).

    Keyword Args:
        token (optional): The token with which to authenticate requests to Context.
            Visit https://with.context.ai/settings to generate a token.
            If not provided, the value of the `CONTEXT_TOKEN` environment
            variable will be used.

    Raises:
        ImportError: if the `context-python` package is not installed.

    Chat Example:
        >>> from samosila.providers.openai import OpenAIProvider
        >>> from samosila.integrations.callbacks import ContextCallbackHandler
        >>> context_callback = ContextCallbackHandler(
        ...     token="<CONTEXT_TOKEN_HERE>",
        ... )
        >>> provider = OpenAIProvider(
        ...     temperature=0,
        ...     headers={"user_id": "123"},
        ...     callbacks=[context_callback],
        ...     openai_api_key="API_KEY_HERE",
        ... )
        >>> messages = [
        ...     SystemMessage(content="You translate English to French."),
        ...     HumanMessage(content="I love programming with LangChain."),
        ... ]
        >>> provider.chat(messages)
    """

    def __init__(
        self,
        token: str = "",
        verbose: bool = False,
        features_state: Optional[FeaturesState] = None,
        **kwargs: Any,
    ) -> None:
        if features_state is None:
            features_state = FeaturesState.only(
                {"on_chat_start": True, "on_chat_end": True})
        super().__init__(features_state)

        (
            self.context,
            self.credential,
            self.conversation_model,
            self.message_model,
            self.message_role_model,
            self.rating_model,
        ) = import_context()

        token = token or os.environ.get("CONTEXT_TOKEN") or ""

        self.client = self.context.ContextAPI(
            credential=self.credential(token))

        self.chain_run_id = None

        self.llm_model = None

        self.messages: List[Any] = []
        self.metadata: Dict[str, str] = {}

    def on_chat_start(self, data: ChatData, **kwargs) -> Any:
        """Run when the chat model is started."""
        llm_model = data.model
        if llm_model is not None:
            self.metadata["model"] = llm_model

        if len(data.messages) == 0:
            return

        for message in data.messages:
            role = self.message_role_model.SYSTEM
            if message.role == "human":
                role = self.message_role_model.USER
            elif message.role == "system":
                role = self.message_role_model.SYSTEM
            elif message.role == "ai":
                role = self.message_role_model.ASSISTANT

            self.messages.append(
                self.message_model(
                    message=message.content,
                    role=role,
                )
            )

    def on_chat_end(self, data: ChatData, **kwargs: Any) -> None:
        """Run when LLM ends."""
        if len(data.response or []) == 0:
            return

        if not self.chain_run_id:
            generation = (data.response or [])[0]
            self.messages.append(
                self.message_model(
                    message=generation.message.content,
                    role=self.message_role_model.ASSISTANT,
                )
            )

            self._log_conversation()

    def _log_conversation(self) -> None:
        """Log the conversation to the context API."""
        if len(self.messages) == 0:
            return

        self.client.log.conversation_upsert(
            body={
                "conversation": self.conversation_model(
                    messages=self.messages,
                    metadata=self.metadata,
                )
            }
        )

        self.messages = []
        self.metadata = {}
