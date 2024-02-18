from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ToolRequest(BaseModel):
    """
    A request to run a tool.

    Attributes:
        name: Name of the tool that the AI wants the client to use.
        arguments: Arguments to pass to the tool. The format must be a JSON Schema-compliant
            object serialized into a string.
    """
    name: str = Field(...)
    arguments: str = Field(...)


class ActionContext(BaseModel):
    """
    The context of the action that the agent is taking.

    Attributes:
        content: The content of the final output of the agent when it no longer needs any tools.
        tool_request: The tool request if the agent needs more information.
    """
    content: Optional[str] = Field(default=None)
    tool_request: Optional[ToolRequest] = Field(
        description="The tool request if the agent needs more information.",
    )


class ToolPropertyValue(BaseModel):
    """
    A schema used to validate a single keyword argument for a tool.

    Attributes:
        type: The argument's type.

            The type is used to help the Agent generate valid arguments for the tool.

            For more information about types, see:
            https://json-schema.org/understanding-json-schema/reference/type.html#type-specific-keywords
        description: Description of what the argument is used for.

            This description is used to help the Agent generate sensible arguments for the tool.
            It is very important that this description is succinct, clear, and accurate.
        default: A default value for the argument if unspecified.
        examples: Example values demonstrating how the argument should look.

            This can be used to help the agent understand what a valid argument should look like.
    """
    type: Literal["string", "number", "integer", "boolean", "object", "array", "null",] = Field(
        ...,
    )
    description: str = Field(
        ...,
    )
    default: Optional[str] = Field(default=None)
    examples: Optional[List[str]] = Field(default=None)

    class Config(BaseModel.Config):
        title = "property"


class ToolArguments(BaseModel):
    """
    An object where each key is the name of a keyword argument and each value is a schema used to
    validate that property. Each schema must have a type and description, but can also have a
    default value and examples.

    For more information on how to define a valid property, visit
    https://json-schema.org/understanding-json-schema/reference/object.html

    Attributes:
        type: Type of argument. Currently only "object" is supported
        properties: An object where each key is the name of a keyword argument and each value is a
            schema used to validate that property. Each schema must have a type and description, but
            can also have a default value and examples.

            For more information on how to define a valid property, visit
            https://json-schema.org/understanding-json-schema/reference/object.html
    """
    type: Literal["object"] = Field(default="object")
    properties: Dict[str, ToolPropertyValue] = Field(default_factory=dict)


class Tool(BaseModel):
    """
    A tool is a function that the Agent has at its disposal. This schema is used to tell the Agent
    about the tools that are available to it.

    Attributes:
        name: Name of the tool.

            The tool name is the name the client wishes the Agent to use to refer to this
            function when it decides if it wants the user to use the tool or not. It must be
            unique amongst the set of tools provided in a single API call.
        description: Description of the tool.

            Because some queries are complex and may require multiple tools to complete, it is
            important to make these descriptions as informative as possible. If a tool is not
            being chosen when it should, it is common practice to tune the description of the
            tool to make it more apparent to the agent when the tool can be used effectively.
        arguments: An JSON Schema-compliant schema for the tool arguments. To describe a
            function that accepts no parameters, provide the value `{"type": "object",
            "properties": {}}`.

            For more information on how to define a valid JSON Schema object, visit
            https://json-schema.org/understanding-json-schema/reference/object.html
    """
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    description: str = Field(...)
    arguments: ToolArguments = Field(...)
