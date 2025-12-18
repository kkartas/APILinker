"""Optional message-queue connector plugins.

These connectors integrate with ApiLinker's plugin system via ConnectorPlugin.
All external dependencies are optional and imported lazily.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from apilinker.core.message_queue import JsonMessageSerializer, MessageEnvelope
from apilinker.core.plugins import ConnectorPlugin

try:
    import pika
except ImportError:  # pragma: no cover
    pika = None

try:
    import redis as redis_lib
except ImportError:  # pragma: no cover
    redis_lib = None

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None

try:
    from kafka import KafkaConsumer, KafkaProducer
except ImportError:  # pragma: no cover
    KafkaConsumer = None
    KafkaProducer = None


def _require(dep: Any, name: str) -> Any:
    if dep is None:
        raise ImportError(
            f"Optional dependency '{name}' is required for this connector. "
            f"Install via: pip install apilinker[mq]"
        )
    return dep


class RabbitMQConnectorPlugin(ConnectorPlugin):
    plugin_name = "rabbitmq"
    plugin_type = "connector"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._serializer = JsonMessageSerializer()

    def connect(
        self,
        *,
        url: Optional[str] = None,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        virtual_host: str = "/",
        heartbeat: int = 60,
        prefetch_count: int = 1,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        pika_mod = _require(pika, "pika")

        if url:
            params = pika_mod.URLParameters(url)
        else:
            credentials = pika_mod.PlainCredentials(username, password)
            params = pika_mod.ConnectionParameters(
                host=host,
                port=port,
                virtual_host=virtual_host,
                credentials=credentials,
                heartbeat=heartbeat,
            )

        connection = pika_mod.BlockingConnection(params)
        channel = connection.channel()
        channel.basic_qos(prefetch_count=max(1, int(prefetch_count)))

        return {"connection": connection, "channel": channel}

    def fetch(
        self,
        connection: Dict[str, Any],
        endpoint: str,
        *,
        auto_ack: bool = False,
        **kwargs: Any,
    ) -> Optional[MessageEnvelope]:
        channel = connection["channel"]
        method_frame, properties, body = channel.basic_get(
            queue=endpoint,
            auto_ack=auto_ack,
        )
        if method_frame is None:
            return None

        raw: bytes = body or b""
        payload = self._serializer.loads(raw)

        delivery_tag = getattr(method_frame, "delivery_tag", None)

        def _ack() -> None:
            if delivery_tag is not None:
                channel.basic_ack(delivery_tag=delivery_tag)

        def _nack(requeue: bool = False) -> None:
            if delivery_tag is not None:
                channel.basic_nack(delivery_tag=delivery_tag, requeue=requeue)

        headers = getattr(properties, "headers", None) or {}
        message_id = getattr(properties, "message_id", None)

        return MessageEnvelope(
            body=payload,
            raw=raw,
            headers=dict(headers),
            attributes={"delivery_tag": delivery_tag},
            source=endpoint,
            message_id=message_id,
            ack=None if auto_ack else _ack,
            nack=None if auto_ack else _nack,
        )

    def send(
        self,
        connection: Dict[str, Any],
        endpoint: str,
        data: Any,
        *,
        exchange: str = "",
        headers: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        pika_mod = _require(pika, "pika")
        channel = connection["channel"]
        body = self._serializer.dumps(data)

        props = pika_mod.BasicProperties(
            content_type="application/json",
            headers=headers or {},
            message_id=message_id,
        )

        channel.basic_publish(
            exchange=exchange,
            routing_key=endpoint,
            body=body,
            properties=props,
        )
        return {"success": True}


class RedisPubSubConnectorPlugin(ConnectorPlugin):
    plugin_name = "redis_pubsub"
    plugin_type = "connector"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._serializer = JsonMessageSerializer()

    def connect(
        self,
        *,
        url: Optional[str] = None,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        redis_mod = _require(redis_lib, "redis")

        if url:
            client = redis_mod.from_url(url)
        else:
            client = redis_mod.Redis(host=host, port=port, db=db, password=password)

        pubsub = client.pubsub(ignore_subscribe_messages=True)
        return {"client": client, "pubsub": pubsub, "subscriptions": set()}

    def fetch(
        self,
        connection: Dict[str, Any],
        endpoint: str,
        *,
        timeout: float = 0.0,
        **kwargs: Any,
    ) -> Optional[MessageEnvelope]:
        pubsub = connection["pubsub"]
        subs = connection["subscriptions"]

        if endpoint not in subs:
            pubsub.subscribe(endpoint)
            subs.add(endpoint)

        msg = pubsub.get_message(timeout=timeout)
        if not msg:
            return None

        raw_data = msg.get("data")
        if isinstance(raw_data, bytes):
            raw = raw_data
        else:
            raw = str(raw_data).encode("utf-8")
        payload = self._serializer.loads(raw)

        return MessageEnvelope(
            body=payload,
            raw=raw,
            headers={},
            attributes={"channel": msg.get("channel")},
            source=endpoint,
        )

    def send(
        self,
        connection: Dict[str, Any],
        endpoint: str,
        data: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        client = connection["client"]
        body = self._serializer.dumps(data)
        client.publish(endpoint, body)
        return {"success": True}


class SQSPubSubConnectorPlugin(ConnectorPlugin):
    plugin_name = "aws_sqs"
    plugin_type = "connector"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._serializer = JsonMessageSerializer()

    def connect(
        self,
        *,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        boto3_mod = _require(boto3, "boto3")
        client = boto3_mod.client(
            "sqs",
            region_name=region_name,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        return {"client": client}

    def fetch(
        self,
        connection: Dict[str, Any],
        endpoint: str,
        *,
        max_messages: int = 1,
        wait_time_seconds: int = 0,
        visibility_timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> List[MessageEnvelope]:
        client = connection["client"]
        params: Dict[str, Any] = {
            "QueueUrl": endpoint,
            "MaxNumberOfMessages": max(1, min(10, int(max_messages))),
            "WaitTimeSeconds": max(0, int(wait_time_seconds)),
            "MessageAttributeNames": ["All"],
            "AttributeNames": ["All"],
        }
        if visibility_timeout is not None:
            params["VisibilityTimeout"] = int(visibility_timeout)

        resp = client.receive_message(**params)
        messages = resp.get("Messages", []) or []

        envelopes: List[MessageEnvelope] = []
        for msg in messages:
            receipt = msg.get("ReceiptHandle")
            body_text = msg.get("Body", "")
            raw = body_text.encode("utf-8")
            payload = self._serializer.loads(raw)

            def _ack(receipt_handle: str = receipt) -> None:
                if receipt_handle:
                    client.delete_message(
                        QueueUrl=endpoint,
                        ReceiptHandle=receipt_handle,
                    )

            envelopes.append(
                MessageEnvelope(
                    body=payload,
                    raw=raw,
                    headers={},
                    attributes={
                        "receipt_handle": receipt,
                        "attributes": msg.get("Attributes", {}),
                        "message_attributes": msg.get("MessageAttributes", {}),
                    },
                    source=endpoint,
                    message_id=msg.get("MessageId"),
                    ack=_ack,
                )
            )

        return envelopes

    def send(
        self,
        connection: Dict[str, Any],
        endpoint: str,
        data: Any,
        *,
        message_attributes: Optional[Dict[str, Any]] = None,
        delay_seconds: int = 0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        client = connection["client"]
        raw = self._serializer.dumps(data)
        resp = client.send_message(
            QueueUrl=endpoint,
            MessageBody=raw.decode("utf-8"),
            DelaySeconds=max(0, int(delay_seconds)),
            MessageAttributes=message_attributes or {},
        )
        return {"success": True, "message_id": resp.get("MessageId")}


class KafkaConnectorPlugin(ConnectorPlugin):
    plugin_name = "kafka"
    plugin_type = "connector"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._serializer = JsonMessageSerializer()

    def connect(
        self,
        *,
        bootstrap_servers: Any = "localhost:9092",
        client_id: str = "apilinker",
        group_id: Optional[str] = None,
        enable_auto_commit: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        consumer_cls = _require(KafkaConsumer, "kafka-python")
        producer_cls = _require(KafkaProducer, "kafka-python")

        producer = producer_cls(
            bootstrap_servers=bootstrap_servers,
            client_id=client_id,
            value_serializer=None,
            key_serializer=None,
        )

        consumer = consumer_cls(
            bootstrap_servers=bootstrap_servers,
            client_id=client_id,
            group_id=group_id,
            enable_auto_commit=enable_auto_commit,
            value_deserializer=None,
            key_deserializer=None,
            auto_offset_reset=kwargs.get("auto_offset_reset", "latest"),
        )

        return {"producer": producer, "consumer": consumer, "subscriptions": set()}

    def fetch(
        self,
        connection: Dict[str, Any],
        endpoint: str,
        *,
        timeout_ms: int = 1000,
        max_records: int = 1,
        **kwargs: Any,
    ) -> Optional[MessageEnvelope]:
        consumer = connection["consumer"]
        subs = connection["subscriptions"]
        if endpoint not in subs:
            consumer.subscribe([endpoint])
            subs.add(endpoint)

        records = consumer.poll(
            timeout_ms=max(0, int(timeout_ms)),
            max_records=max(1, int(max_records)),
        )
        if not records:
            return None

        msg = None
        for _tp, msgs in records.items():
            if msgs:
                msg = msgs[0]
                break
        if msg is None:
            return None

        raw_value = getattr(msg, "value", b"") or b""
        payload = self._serializer.loads(raw_value)

        def _ack() -> None:
            try:
                consumer.commit()
            except Exception:
                # If auto-commit is enabled or commit is unsupported, we treat ack as a no-op.
                return

        return MessageEnvelope(
            body=payload,
            raw=raw_value,
            headers={},
            attributes={
                "topic": getattr(msg, "topic", None),
                "partition": getattr(msg, "partition", None),
                "offset": getattr(msg, "offset", None),
                "key": getattr(msg, "key", None),
            },
            source=endpoint,
            message_id=None,
            ack=_ack,
        )

    def send(
        self,
        connection: Dict[str, Any],
        endpoint: str,
        data: Any,
        *,
        key: Optional[bytes] = None,
        sync: bool = True,
        timeout: float = 10.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        producer = connection["producer"]
        raw = self._serializer.dumps(data)
        future = producer.send(endpoint, value=raw, key=key)
        if sync:
            record_md = future.get(timeout=timeout)
            return {
                "success": True,
                "topic": getattr(record_md, "topic", endpoint),
                "partition": getattr(record_md, "partition", None),
                "offset": getattr(record_md, "offset", None),
            }
        return {"success": True}
