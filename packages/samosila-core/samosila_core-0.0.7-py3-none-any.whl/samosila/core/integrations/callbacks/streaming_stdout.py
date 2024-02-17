import sys
from typing import Any, Optional

from ...types import (
    FeaturesState, CallbackHandler
)


class StreamingStdOutCallbackHandler(CallbackHandler):

    def __init__(
        self,
        features_state: Optional[FeaturesState] = None,
    ) -> None:
        if features_state is None:
            features_state = FeaturesState.only(
                {"on_llm_new_token": True})
        super().__init__(features_state)

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        sys.stdout.write(token + " ")
        sys.stdout.flush()
