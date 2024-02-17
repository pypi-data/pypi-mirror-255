# flake8: noqa
from typing import Any, List, Optional

from ...types import (
    FeaturesState, ChatData,
    CallbackHandler, CompletionData
)


class DeepEvalCallbackHandler(CallbackHandler):
    """Callback Handler that logs into deepeval.

    Args:
        implementation_name: name of the `implementation` in deepeval
        metrics: A list of metrics

    Raises:
        ImportError: if the `deepeval` package is not installed.

    Examples:
        >>> from samosila.providers.openai import OpenAIProvider
        >>> from samosila.integrations.callbacks import DeepEvalCallbackHandler
        >>> from deepeval.metrics import AnswerRelevancy
        >>> metric = AnswerRelevancy(minimum_score=0.3)
        >>> deepeval_callback = DeepEvalCallbackHandler(
        ...     implementation_name="exampleImplementation",
        ...     metrics=[metric],
        ... )
        >>> openai = OpenAIProvider(
        ...     temperature=0,
        ...     callbacks=[deepeval_callback],
        ...     verbose=True,
        ...     openai_api_key="API_KEY_HERE",
        ... )
        >>> openai.generate([
        ...     "What is the best evaluation tool out there? (no bias at all)",
        ... ])
        "Deepeval, no doubt about it."
    """

    REPO_URL: str = "https://github.com/confident-ai/deepeval"
    ISSUES_URL: str = f"{REPO_URL}/issues"

    def __init__(
        self,
        metrics: List[Any],
        implementation_name: Optional[str] = None,
        features_state: Optional[FeaturesState] = None,
    ) -> None:

        if features_state is None:
            features_state = FeaturesState.only(
                {"on_llm_end": True, "on_chat_end": True})
        super().__init__(features_state)

        try:
            import deepeval
        except ImportError:
            raise ImportError(
                """To use the deepeval callback manager you need to have the 
                `deepeval` Python package installed. Please install it with 
                `pip install deepeval`"""
            )

        self.implementation_name = implementation_name
        self.metrics = metrics

    def on_llm_end(self, data: CompletionData, **kwargs) -> None:
        """Log records to deepeval when an LLM ends."""
        from deepeval.metrics.base_metric import LLMTestCase

        print("Sending Data to DeepEval")
        for metric in self.metrics:
            for i, generation in enumerate(data.response or []):
                metric.measure(
                    LLMTestCase(
                        input=data.prompt.content,
                        actual_output=generation.text
                    )
                )

    def on_chat_end(self, data: ChatData, **kwargs) -> None:
        """Log records to deepeval when an LLM ends."""
        from deepeval.metrics.base_metric import LLMTestCase

        print("Sending Data to DeepEval")
        for metric in self.metrics:
            for i, generation in enumerate(data.response or []):
                metric.measure(
                    LLMTestCase(
                        input="\n".join([x.content for x in data.messages]),
                        actual_output=generation.message.content or ''
                    )
                )
