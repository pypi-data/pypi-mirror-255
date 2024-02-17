from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from .response_types import (
  AIMessage,
  BaseMessage,
  HumanMessage,
  SystemMessage,
)

class BaseChatMessageHistory(ABC):

    messages: List[BaseMessage]

    def add_user_message(self, message: str) -> None:
        self.add_message(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self.add_message(AIMessage(content=message))

    @abstractmethod
    def add_message(self, message: BaseMessage) -> None:
        raise NotImplementedError()

    @abstractmethod
    def clear(self) -> None:
        """Remove all messages from the store"""

    def __str__(self) -> str:
        return get_buffer_string(self.messages)


def get_buffer_string(
    messages: Sequence[BaseMessage], human_prefix: str = "Human", ai_prefix: str = "AI"
) -> str:
    string_messages = []
    for m in messages:
        if isinstance(m, HumanMessage):
            role = human_prefix
        elif isinstance(m, AIMessage):
            role = ai_prefix
        elif isinstance(m, SystemMessage):
            role = "System"
        else:
            raise ValueError(f"Got unsupported message type: {m}")
        message = f"{role}: {m.content}"
        if isinstance(m, AIMessage) and "function_call" in m.additional_kwargs:
            message += f"{m.additional_kwargs['function_call']}"
        string_messages.append(message)

    return "\n".join(string_messages)
