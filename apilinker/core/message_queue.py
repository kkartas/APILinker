"""
Message queue utilities for event-driven pipelines.

This module is intentionally dependency-free and provides shared primitives
used by optional message-queue connectors.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Union,
)

from apilinker.core.error_handling import (
    ApiLinkerError,
    DeadLetterQueue,
    ErrorCategory,
)

logger = logging.getLogger(__name__)


JsonLike = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


class MessageSerializer(Protocol):
    def dumps(self, payload: Any) -> bytes:
        pass

    def loads(self, payload: Union[bytes, str]) -> Any:
        pass


class JsonMessageSerializer:
    def dumps(self, payload: Any) -> bytes:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, str):
            return payload.encode("utf-8")
        return json.dumps(payload, default=str).encode("utf-8")

    def loads(self, payload: Union[bytes, str]) -> Any:
        if isinstance(payload, bytes):
            text = payload.decode("utf-8")
        else:
            text = payload
        try:
            return json.loads(text)
        except Exception:
            return text


@dataclass
class MessageEnvelope:
    body: Any
    raw: Optional[bytes] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    message_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ack: Optional[Callable[[], None]] = None
    nack: Optional[Callable[[bool], None]] = None

    def ack_message(self) -> None:
        if self.ack is not None:
            self.ack()

    def nack_message(self, requeue: bool = False) -> None:
        if self.nack is not None:
            self.nack(requeue)


Predicate = Callable[[MessageEnvelope, Any], bool]
Transformer = Callable[[Any, MessageEnvelope], Any]


class MessageRouter:
    def __init__(self, routes: Optional[Sequence[Tuple[Predicate, str]]] = None):
        self._routes: List[Tuple[Predicate, str]] = list(routes or [])

    def add_route(self, predicate: Predicate, destination: str) -> None:
        self._routes.append((predicate, destination))

    def route(
        self,
        envelope: MessageEnvelope,
        payload: Any,
        default: Optional[str] = None,
    ) -> str:
        for predicate, dest in self._routes:
            try:
                if predicate(envelope, payload):
                    return dest
            except Exception:
                continue
        if default is None:
            raise ValueError("No route matched and no default destination provided")
        return default


class Consumer(Protocol):
    def fetch(self, connection: Any, endpoint: str, **kwargs: Any) -> Any:
        pass


class Producer(Protocol):
    def send(self, connection: Any, endpoint: str, data: Any, **kwargs: Any) -> Any:
        pass


class MessagePipeline:
    def __init__(
        self,
        consumer: Consumer,
        producer: Producer,
        *,
        transformer: Optional[Transformer] = None,
        router: Optional[MessageRouter] = None,
        dlq: Optional[DeadLetterQueue] = None,
    ) -> None:
        self.consumer = consumer
        self.producer = producer
        self.transformer = transformer
        self.router = router
        self.dlq = dlq

    def process_once(
        self,
        *,
        consumer_connection: Any,
        producer_connection: Any,
        source: str,
        default_destination: Optional[str] = None,
        fetch_kwargs: Optional[Dict[str, Any]] = None,
        send_kwargs: Optional[Dict[str, Any]] = None,
        max_messages: int = 1,
        operation_type: str = "message_pipeline",
    ) -> Dict[str, Any]:
        fetch_kwargs = fetch_kwargs or {}
        send_kwargs = send_kwargs or {}

        raw_result = self.consumer.fetch(consumer_connection, source, **fetch_kwargs)

        envelopes: List[MessageEnvelope] = []
        if raw_result is None:
            envelopes = []
        elif isinstance(raw_result, MessageEnvelope):
            envelopes = [raw_result]
        elif isinstance(raw_result, list) and all(
            isinstance(x, MessageEnvelope) for x in raw_result
        ):
            envelopes = list(raw_result)
        else:
            envelopes = [MessageEnvelope(body=raw_result, source=source)]

        processed = 0
        sent = 0
        failed = 0
        failures: List[Dict[str, Any]] = []

        for env in envelopes[: max(0, int(max_messages))]:
            processed += 1
            try:
                payload = env.body
                if self.transformer is not None:
                    payload = self.transformer(payload, env)

                destination = default_destination
                if self.router is not None:
                    destination = self.router.route(
                        env,
                        payload,
                        default=default_destination,
                    )
                if destination is None:
                    destination = source

                self.producer.send(
                    producer_connection,
                    destination,
                    payload,
                    **send_kwargs,
                )
                env.ack_message()
                sent += 1
            except Exception as exc:
                failed += 1
                env.nack_message(requeue=False)

                err = ApiLinkerError(
                    message=str(exc),
                    error_category=ErrorCategory.PLUGIN,
                    additional_context={
                        "source": source,
                        "destination": default_destination,
                        "message_id": env.message_id,
                        "operation_type": operation_type,
                    },
                )

                if self.dlq is not None:
                    try:
                        self.dlq.add_item(
                            err,
                            payload={
                                "body": env.body,
                                "headers": env.headers,
                                "attributes": env.attributes,
                                "source": env.source,
                                "message_id": env.message_id,
                            },
                            metadata={"operation_type": operation_type},
                        )
                    except Exception as dlq_exc:
                        logger.warning("Failed to write message to DLQ: %s", dlq_exc)

                failures.append(err.to_dict())

        return {
            "processed": processed,
            "sent": sent,
            "failed": failed,
            "failures": failures,
        }
