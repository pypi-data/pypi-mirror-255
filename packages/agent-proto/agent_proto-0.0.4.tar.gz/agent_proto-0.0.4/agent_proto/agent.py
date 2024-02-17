"""
Agent module.
it can be run locally and interacted with via a chat interface.
The agent can be used to run tools based on user input.
The agent is trained to provide useful responses and guidance to the user.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterable, Literal, Optional, Type, TypeVar

from pydantic import BaseModel

from .proxy import LazyProxy
from .tool import Tool, ToolDefinition, ToolOutput

T_co = TypeVar("T_co", covariant=True)


class Message(BaseModel):
    """
    Represents a message with a role and content.

    Attributes:
        role (Literal["user", "assistant"]): The role of the message sender.
        content (str): The content of the message.
    """

    role: Literal["user", "assistant"]
    content: str


class BaseAgent(BaseModel, LazyProxy[T_co], ABC):
    """
    Abstract base class for agents.
    """

    messages: list[Message]
    model: str
    tools: Iterable[Type[Tool]]

    @abstractmethod
    async def chat(
        self, *, message: str, stream: bool = True
    ) -> AsyncIterator[Message] | Message:
        """
        Chat with the agent.

        Args:
            message (str): The message to send to the agent.
            stream (bool, optional): Whether to stream the messages or not. Defaults to True.

        Returns:
            AsyncIterator[Message] | Message: An async iterator of messages or a single message.
        """
        raise NotImplementedError

    @abstractmethod
    async def run(
        self, *, message: str, definitions: Optional[Iterable[ToolDefinition]] = None
    ) -> ToolOutput:
        """
        Run the agent.

        Args:
            message (str): The message to run the agent with.

        Returns:
            ToolOutput: The output of the agent's run.
        """
        raise NotImplementedError

    @abstractmethod
    def __call__(self) -> T_co:
        """
        Call the agent.

        Returns:
            T_co: The agent api implementation.
        """
        raise NotImplementedError

    def __load__(self) -> T_co:
        """
        Load the agent.

        Returns:
            T_co: The agent.
        """
        return self.__call__()
