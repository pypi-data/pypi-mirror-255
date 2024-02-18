from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from scale_egp.utils.model_utils import RootModel


class ToolRequest(BaseModel):
    """
    Describes a request to run a tool

    Attributes:
        name: Name of the tool
        arguments: Arguments (JSON serializable string) to pass to the tool
    """
    name: str  # Name of the tool
    arguments: str  # Arguments (JSON serializable string) to pass to the tool


class AgentMessage(BaseModel):
    """
    Message from an agent

    Attributes:
        role: The role of the message, must be "agent"
        content: Output of the agent if finished
        tool_request: Request to run a tool
    """
    role: Literal["agent"] = "agent"
    content: Optional[str] = None  # Output of the agent if finished
    tool_request: Optional[ToolRequest] = None  # Request to run a tool


class ToolMessage(BaseModel):
    """
    Message from a tool

    Attributes:
        role: The role of the message, must be "tool"
        name: Name of the tool
        content: Output of calling the tool (JSON serialized to string)
    """
    role: Literal["tool"] = "tool"
    name: str  # Name of the tool
    content: str  # Output of calling the tool (JSON serialized to string)


class UserMessage(BaseModel):
    """
    Message from the user

    Attributes:
        role: The role of the message, must be "user"
        content: The content of the message
    """
    role: Literal["user"] = "user"
    content: str


class AssistantMessage(BaseModel):
    """
    Message from a non-agent AI.

    Attributes:
        role: The role of the message, must be "assistant"
        content: The content of the message
    """
    role: Literal["assistant"] = "assistant"
    content: str


class SystemMessage(BaseModel):
    """
    Message from the system. This is used if this message did not originate from the user or AI.

    Attributes:
        role: The role of the message, must be "system"
        content: The content of the message
    """
    role: Literal["system"] = "system"
    content: str


class Message(RootModel):
    """
    A type alias for a Union of all message types.

    Attributes:
        __root__: Instead of directly using this class, please use the appropriate message type
            for your use case.
    """
    __root__: Union[UserMessage, ToolMessage, AgentMessage, AssistantMessage, SystemMessage] = (
        Field(..., discriminator="role")
    )

