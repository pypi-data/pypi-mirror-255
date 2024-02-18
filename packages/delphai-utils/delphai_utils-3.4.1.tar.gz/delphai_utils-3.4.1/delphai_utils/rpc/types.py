import aio_pika.message
import pydantic
import time
import uuid

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Any, Optional, Union

from .models import BaseModel


class AbstractOptions(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    def __init__(self, *args: "AbstractOptions", **kwargs: Dict[str, Any]):
        if args:
            merged = {}
            self_class = type(self)
            for options in args:
                if not isinstance(options, self_class):
                    raise TypeError(
                        f"Positional arguments must be {self_class} instances"
                    )

                merged.update(options.model_dump(exclude_unset=True))
            merged.update(**kwargs)

            kwargs = merged

        return super().__init__(**kwargs)

    def update(self, *args: "AbstractOptions", **kwargs: Dict[str, Any]):
        if not args and not kwargs:
            return self

        return self.__class__(self, *args, **kwargs)


class Priority(IntEnum):
    LOW = 0
    NORMAL = 1
    DEFAULT = 1
    HIGH = 2
    INTERACTIVE = 3
    SYSTEM = 4


class Message(aio_pika.message.Message):
    """AMQP message abstraction"""

    __slots__ = ()

    def __init__(
        self,
        body: Union[bytes, BaseModel],
        *,
        headers: Optional[aio_pika.message.HeadersType] = None,
        content_type: Optional[str] = None,
        content_encoding: Optional[str] = None,
        delivery_mode: Union[aio_pika.message.DeliveryMode, int, None] = None,
        priority: Optional[int] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        expiration: Optional[aio_pika.message.DateType] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[aio_pika.message.DateType] = None,
        type: Optional[str] = None,
        user_id: Optional[str] = None,
        app_id: Optional[str] = None,
    ):
        if isinstance(body, BaseModel):
            body = body.model_dump_msgpack()
            content_type = None

        super().__init__(
            body=body,
            headers=headers,
            content_type=content_type or "application/msgpack",
            content_encoding=content_encoding,
            delivery_mode=delivery_mode or aio_pika.DeliveryMode.PERSISTENT,
            priority=priority,
            correlation_id=correlation_id,
            reply_to=reply_to,
            expiration=expiration,
            message_id=message_id or str(uuid.uuid1()),
            timestamp=timestamp or time.time(),
            type=type,
            user_id=user_id,
            app_id=app_id,
        )


@dataclass(frozen=True)
class RequestContext:
    deadline: Optional[float]
    priority: Priority
