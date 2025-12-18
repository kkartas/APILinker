from apilinker.core.error_handling import DeadLetterQueue
from apilinker.core.message_queue import (
    JsonMessageSerializer,
    MessageEnvelope,
    MessagePipeline,
    MessageRouter,
)


class DummyConsumer:
    def __init__(self, result):
        self._result = result

    def fetch(self, connection, endpoint, **kwargs):
        return self._result


class DummyProducer:
    def __init__(self):
        self.sent = []

    def send(self, connection, endpoint, data, **kwargs):
        self.sent.append((endpoint, data))
        return {"success": True}


def test_serializer_roundtrip_json():
    s = JsonMessageSerializer()
    data = {"a": 1}
    raw = s.dumps(data)
    assert isinstance(raw, (bytes, bytearray))
    out = s.loads(raw)
    assert out == data


def test_pipeline_process_once_transform_and_route(tmp_path):
    acked = {"n": 0}

    def ack():
        acked["n"] += 1

    env = MessageEnvelope(body={"kind": "x", "value": 1}, source="in", ack=ack)

    consumer = DummyConsumer(env)
    producer = DummyProducer()

    def transform(payload, envelope):
        payload["value"] += 1
        return payload

    router = MessageRouter([(lambda env, payload: payload.get("kind") == "x", "topic_x")])

    pipeline = MessagePipeline(
        consumer,
        producer,
        transformer=transform,
        router=router,
        dlq=DeadLetterQueue(str(tmp_path / "dlq")),
    )

    result = pipeline.process_once(
        consumer_connection={},
        producer_connection={},
        source="in",
        default_destination="fallback",
    )

    assert result["processed"] == 1
    assert result["sent"] == 1
    assert result["failed"] == 0
    assert producer.sent == [("topic_x", {"kind": "x", "value": 2})]
    assert acked["n"] == 1


def test_pipeline_writes_to_dlq_on_failure(tmp_path):
    nacked = {"n": 0}

    def nack(requeue=False):
        nacked["n"] += 1

    env = MessageEnvelope(body={"x": 1}, source="in", nack=nack)

    consumer = DummyConsumer(env)
    producer = DummyProducer()

    def transform(payload, envelope):
        raise RuntimeError("boom")

    dlq_dir = tmp_path / "dlq"
    dlq = DeadLetterQueue(str(dlq_dir))

    pipeline = MessagePipeline(consumer, producer, transformer=transform, dlq=dlq)
    result = pipeline.process_once(
        consumer_connection={},
        producer_connection={},
        source="in",
        default_destination="out",
    )

    assert result["processed"] == 1
    assert result["sent"] == 0
    assert result["failed"] == 1
    assert nacked["n"] == 1
    # DLQ should have at least one file
    assert list(dlq_dir.glob("*.json"))
