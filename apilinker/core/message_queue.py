"""
Message queue utilities for event-driven pipelines.

This module is intentionally dependency-free and provides shared primitives
used by optional message-queue connectors.
"""

from __future__ import annotations

import json
import logging
import random
import threading
import time
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


def _safe_close(obj: Any) -> None:
    if obj is None:
        return
    if isinstance(obj, dict):
        for v in obj.values():
            _safe_close(v)
        return
    close_fn = getattr(obj, "close", None)
    if callable(close_fn):
        try:
            close_fn()
        except Exception:
            pass
    disconnect_fn = getattr(obj, "disconnect", None)
    if callable(disconnect_fn):
        try:
            disconnect_fn()
        except Exception:
            pass


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 0.5
    max_delay_seconds: float = 30.0
    backoff_multiplier: float = 2.0
    jitter_seconds: float = 0.1


@dataclass
class IdleBackoffPolicy:
    initial_sleep_seconds: float = 0.1
    max_sleep_seconds: float = 5.0
    backoff_multiplier: float = 2.0


class MessageWorker:
    def __init__(
        self,
        pipeline: MessagePipeline,
        *,
        consumer_connection: Any,
        producer_connection: Any,
        source: str,
        default_destination: Optional[str] = None,
        fetch_kwargs: Optional[Dict[str, Any]] = None,
        send_kwargs: Optional[Dict[str, Any]] = None,
        max_messages_per_poll: int = 1,
        retry_policy: Optional[RetryPolicy] = None,
        idle_backoff: Optional[IdleBackoffPolicy] = None,
        stop_event: Optional[threading.Event] = None,
        operation_type: str = "message_worker",
    ) -> None:
        self.pipeline = pipeline
        self.consumer_connection = consumer_connection
        self.producer_connection = producer_connection
        self.source = source
        self.default_destination = default_destination
        self.fetch_kwargs = fetch_kwargs or {}
        self.send_kwargs = send_kwargs or {}
        self.max_messages_per_poll = max(1, int(max_messages_per_poll))
        self.retry_policy = retry_policy or RetryPolicy()
        self.idle_backoff = idle_backoff or IdleBackoffPolicy()
        self.stop_event = stop_event or threading.Event()
        self.operation_type = operation_type

    def stop(self) -> None:
        self.stop_event.set()

    def close(self) -> None:
        _safe_close(self.consumer_connection)
        _safe_close(self.producer_connection)

    def run(self, *, max_loops: Optional[int] = None) -> Dict[str, Any]:
        processed_total = 0
        sent_total = 0
        failed_total = 0
        dlq_total = 0

        idle_sleep = max(0.0, float(self.idle_backoff.initial_sleep_seconds))
        loops = 0

        try:
            while not self.stop_event.is_set():
                if max_loops is not None and loops >= max_loops:
                    break
                loops += 1

                try:
                    raw_result = self.pipeline.consumer.fetch(
                        self.consumer_connection,
                        self.source,
                        **self.fetch_kwargs,
                    )
                except Exception as exc:
                    logger.warning("Consumer fetch failed: %s", exc)
                    time.sleep(idle_sleep)
                    idle_sleep = min(
                        float(self.idle_backoff.max_sleep_seconds),
                        idle_sleep * float(self.idle_backoff.backoff_multiplier or 1.0),
                    )
                    continue

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
                    envelopes = [MessageEnvelope(body=raw_result, source=self.source)]

                if not envelopes:
                    time.sleep(idle_sleep)
                    idle_sleep = min(
                        float(self.idle_backoff.max_sleep_seconds),
                        idle_sleep * float(self.idle_backoff.backoff_multiplier or 1.0),
                    )
                    continue

                idle_sleep = max(0.0, float(self.idle_backoff.initial_sleep_seconds))

                for env in envelopes[: self.max_messages_per_poll]:
                    processed_total += 1
                    ok, dlq_written = self._handle_envelope(env)
                    if ok:
                        sent_total += 1
                    else:
                        failed_total += 1
                    if dlq_written:
                        dlq_total += 1

        finally:
            self.close()

        return {
            "processed": processed_total,
            "sent": sent_total,
            "failed": failed_total,
            "dlq_written": dlq_total,
            "loops": loops,
        }

    def _handle_envelope(self, env: MessageEnvelope) -> Tuple[bool, bool]:
        attempts = 0
        last_exc: Optional[Exception] = None

        max_attempts = max(1, int(self.retry_policy.max_attempts))
        delay = max(0.0, float(self.retry_policy.initial_delay_seconds))

        while attempts < max_attempts and not self.stop_event.is_set():
            attempts += 1
            try:
                payload = env.body
                if self.pipeline.transformer is not None:
                    payload = self.pipeline.transformer(payload, env)

                destination = self.default_destination
                if self.pipeline.router is not None:
                    destination = self.pipeline.router.route(
                        env,
                        payload,
                        default=self.default_destination,
                    )
                if destination is None:
                    destination = self.source

                self.pipeline.producer.send(
                    self.producer_connection,
                    destination,
                    payload,
                    **self.send_kwargs,
                )
                env.ack_message()
                return True, False
            except Exception as exc:
                last_exc = exc
                if attempts >= max_attempts:
                    break

                jitter = random.uniform(
                    0.0,
                    max(0.0, float(self.retry_policy.jitter_seconds)),
                )
                time.sleep(
                    min(
                        delay + jitter,
                        float(self.retry_policy.max_delay_seconds),
                    )
                )
                delay = min(
                    float(self.retry_policy.max_delay_seconds),
                    delay * float(self.retry_policy.backoff_multiplier or 1.0),
                )

        env.nack_message(requeue=False)

        dlq_written = False
        if self.pipeline.dlq is not None:
            try:
                err = ApiLinkerError(
                    message=str(last_exc) if last_exc is not None else "unknown error",
                    error_category=ErrorCategory.PLUGIN,
                    additional_context={
                        "source": self.source,
                        "destination": self.default_destination,
                        "message_id": env.message_id,
                        "operation_type": self.operation_type,
                        "attempts": attempts,
                    },
                )
                self.pipeline.dlq.add_item(
                    err,
                    payload={
                        "body": env.body,
                        "headers": env.headers,
                        "attributes": env.attributes,
                        "source": env.source,
                        "message_id": env.message_id,
                    },
                    metadata={
                        "operation_type": self.operation_type,
                        "attempts": attempts,
                    },
                )
                dlq_written = True
            except Exception as dlq_exc:
                logger.warning("Failed to write message to DLQ: %s", dlq_exc)

        return False, dlq_written
