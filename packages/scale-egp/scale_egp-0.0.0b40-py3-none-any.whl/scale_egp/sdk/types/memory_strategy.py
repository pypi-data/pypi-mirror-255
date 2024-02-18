from typing import Literal

from pydantic import BaseModel, Field


# Memory Strategies
class LastKMemoryStrategyParams(BaseModel):
    """
    Parameters for the last k memory strategy

    Attributes:
        k: The maximum number of previous messages to remember.
    """
    k: int = Field(
        ...,
        ge=1,
    )


class LastKMemoryStrategy(BaseModel):
    """
    Last K Memory Strategy. This strategy truncates the message history to the last `k`
    messages. It is the simplest way to prevent the model's context limit from being
    exceeded. However, this strategy only allows the model to have short term memory.
    For longer term memory, please use one of the other strategies.

    Attributes:
        name: Name of the memory strategy. Must be `last_k`.
        params: Configuration parameters for the memory strategy.
    """
    name: Literal["last_k"] = Field(
        default="last_k",
        const=True,
    )
    params: LastKMemoryStrategyParams = Field(...)

    class Config(BaseModel.Config):
        title = "Last K Memory Strategy"


MemoryStrategy = LastKMemoryStrategy
