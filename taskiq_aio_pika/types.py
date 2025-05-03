from enum import Enum
from typing import Literal, Optional, TypedDict

from aiormq.abc import TimeoutType


class QueueType(str, Enum):
    CLASSIC = "classic"
    QUORUM = "quorum"


CommonQueueArgs = TypedDict(
    "CommonQueueArgs",
    {
        "x-queue-leader-locator": Literal["client-local", "balanced"],
        "x-max-length-bytes": int,
    },
    total=False,
)


SharedClassicAndQuorumQueueArgs = TypedDict(
    "SharedClassicAndQuorumQueueArgs",
    {
        "x-expires": int,
        "x-message-ttl": int,
        "x-single-active-consumer": bool,
        "x-dead-letter-exchange": str,
        "x-dead-letter-routing-key": str,
        "x-max-length": int,
    },
    total=False,
)


ClassicQueueSpecificArgs = TypedDict(
    "ClassicQueueSpecificArgs",
    {
        "x-queue-type": Literal[QueueType.CLASSIC],
        "x-overflow": Literal["drop-head", "reject-publish", "reject-publish-dlx"],
        "x-queue-master-locator": Literal["client-local", "balanced"],
        "x-max-priority": int,
        "x-queue-mode": Literal["default", "lazy"],
        "x-queue-version": int,
    },
    total=False,
)


QuorumQueueSpecificArgs = TypedDict(
    "QuorumQueueSpecificArgs",
    {
        "x-queue-type": Literal["quorum"],
        "x-overflow": Literal["drop-head", "reject-publish"],
        "x-delivery-limit": int,
        "x-quorum-initial-group-size": int,
        "x-quorum-target-group-size": int,
        "x-dead-letter-strategy": Literal["at-most-once", "at-least-once"],
        "x-max-in-memory-length": int,
        "x-max-in-memory-bytes": int,
    },
    total=False,
)


class ClassicQueueArgs(
    CommonQueueArgs,
    SharedClassicAndQuorumQueueArgs,
    ClassicQueueSpecificArgs,
):
    """rabbitmq-server/deps/rabbit/src/rabbit_classic_queue.erl."""

    pass


class QuorumQueueArgs(
    CommonQueueArgs,
    SharedClassicAndQuorumQueueArgs,
    QuorumQueueSpecificArgs,
):
    """rabbitmq-server/deps/rabbit/src/rabbit_quorum_queue.erl."""

    pass


DeclareQueueKwargs = TypedDict(
    "DeclareQueueKwargs",
    {
        "name": Optional[str],
        "durable": bool,
        "exclusive": bool,
        "passive": bool,
        "auto_delete": bool,
        "timeout": TimeoutType,
        "robust": bool,
    },
    total=False,
)


QuorumQueueDeclareQueueKwargs = TypedDict(
    "QuorumQueueDeclareQueueKwargs",
    {
        "name": Optional[str],
        "durable": Literal[True],
        "exclusive": bool,
        "passive": bool,
        "auto_delete": bool,
        "timeout": TimeoutType,
        "robust": bool,
    },
    total=False,
)
