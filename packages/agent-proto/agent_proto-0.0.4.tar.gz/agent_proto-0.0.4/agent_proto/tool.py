"""
Tool module.
A tool is a pydantic object that embodies an specific feature that can be executed by the agent. It's structure defines the signature of the function that will be implemented on the `run` method, which will contain the core logic of the feature, it automatically handles the schema definition that is needed by the agent to infer which function to call based on user's natural language input.
"""

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, TypedDict

from pydantic import BaseModel, ConfigDict

from .utils import robust, setup_logging

logger = setup_logging(__name__)


class ToolDefinition(TypedDict):
    """
    Represents the definition of a tool.

    Attributes:
        title (str): The title of the tool.
        type (str): The type of the tool.
        description (str): The description of the tool.
        properties (dict[str, object]): The properties of the tool.
        required (list[str]): The required properties of the tool.
    """

    title: str
    type: str
    description: str
    properties: dict[str, object]
    required: list[str]


class ToolOutput(BaseModel):
    """
    Represents a response from a tool.

    Attributes:
        content (Any): The content of the response.
        [TODO] Implement output parser class to handle the output `content` of the tools.
        role (str): The role of the response.
    """

    content: Any
    role: str
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class Tool(BaseModel, ABC):
    """
    Represents a tool used in the application.

    This class provides a base implementation for defining tools.
    Subclasses should override the `run` method to provide the specific
    functionality of the tool.

    Attributes:
        None

    Methods:
        definition: Returns the definition of the tool.
        run: Executes the tool and returns the result. [TODO] Add the output parser here.
        __call__: Executes the tool and returns the result as a ToolOutput object.

    """

    @classmethod
    @lru_cache
    def definition(cls) -> ToolDefinition:
        """
        Returns the definition of the tool as a ToolDefinition object.

        :return: ToolDefinition object representing the tool definition.
        """
        assert isinstance(
            cls.__doc__, str
        ), "All tools must have a docstring explaining its purpose"
        _schema = cls.model_json_schema()
        return {
            "title": cls.__name__,
            "type": "object",
            "description": cls.__doc__,
            "properties": _schema.get("properties", {}),
            "required": _schema.get("required", []),
        }

    @abstractmethod
    async def run(self) -> Any:
        """
        This method is responsible for executing the tool.

        Returns:
            ToolResponse: The response from the tool execution.
        """
        raise NotImplementedError

    @robust
    async def __call__(self) -> ToolOutput:
        """
        This method is intended to be called by the agent.
        It execute the underlying logic of the tool and returns and object with the result as the `content` attribute and the name of the tool as the `role` attribute in order to be compatible with the `message` format used by the agent and easily distinguishable from other messages to be consumed from the client application. It has a `robust` decorator that catches any exception, handles logging and retries the execution of the tool if it fails on an exponential backoff fashion.
        """
        response = await self.run()
        logger.info("Tool %s executed successfully", response)
        return ToolOutput(content=response, role=self.__class__.__name__.lower())
