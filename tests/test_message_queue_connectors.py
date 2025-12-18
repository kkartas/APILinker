from types import SimpleNamespace

import pytest

import apilinker.core.message_queue_connectors as mq
from apilinker.core.message_queue import MessageEnvelope


def test_rabbitmq_plugin_requires_dependency(monkeypatch):
    monkeypatch.setattr(mq, "pika", None)
    plugin = mq.RabbitMQConnectorPlugin()
    with pytest.raises(ImportError):
        plugin.connect(host="localhost")


def test_rabbitmq_fetch_and_send_with_stubbed_pika(monkeypatch):
    class StubMethod:
        delivery_tag = 123

    class StubProps:
        def __init__(self):
            self.headers = {"h": "v"}
            self.message_id = "mid"

    class StubChannel:
        def __init__(self):
            self.acked = []
            self.nacked = []
            self.published = []

        def basic_qos(self, prefetch_count):
            self.prefetch = prefetch_count

        def basic_get(self, queue, auto_ack=False):
            return StubMethod(), StubProps(), b"{\"a\": 1}"

        def basic_ack(self, delivery_tag):
            self.acked.append(delivery_tag)

        def basic_nack(self, delivery_tag, requeue=False):
            self.nacked.append((delivery_tag, requeue))

        def basic_publish(self, exchange, routing_key, body, properties):
            self.published.append((exchange, routing_key, body, properties))

    class StubConn:
        def __init__(self, params):
            self.params = params
            self._channel = StubChannel()

        def channel(self):
            return self._channel

    class StubPika:
        class URLParameters:
            def __init__(self, url):
                self.url = url

        class PlainCredentials:
            def __init__(self, u, p):
                self.u = u
                self.p = p

        class ConnectionParameters:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class BasicProperties:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class BlockingConnection:
            def __init__(self, params):
                self._inner = StubConn(params)

            def channel(self):
                return self._inner.channel()

    monkeypatch.setattr(mq, "pika", StubPika)

    plugin = mq.RabbitMQConnectorPlugin()
    conn = plugin.connect(host="localhost", prefetch_count=2)

    env = plugin.fetch(conn, "q")
    assert isinstance(env, MessageEnvelope)
    assert env.body == {"a": 1}
    env.ack_message()
    assert conn["channel"].acked == [123]

    plugin.send(conn, "q2", {"b": 2})
    assert conn["channel"].published


def test_redis_pubsub_requires_dependency(monkeypatch):
    monkeypatch.setattr(mq, "redis_lib", None)
    plugin = mq.RedisPubSubConnectorPlugin()
    with pytest.raises(ImportError):
        plugin.connect(host="localhost")


def test_redis_pubsub_fetch_and_send_with_stubbed_redis(monkeypatch):
    class StubPubSub:
        def __init__(self):
            self.subscribed = []
            self._msg = {"channel": b"c", "data": b"{\"x\": 1}"}

        def subscribe(self, channel):
            self.subscribed.append(channel)

        def get_message(self, timeout=0.0):
            m = self._msg
            self._msg = None
            return m

    class StubRedis:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.published = []
            self._pubsub = StubPubSub()

        def pubsub(self, ignore_subscribe_messages=True):
            return self._pubsub

        def publish(self, channel, body):
            self.published.append((channel, body))

    class StubRedisLib:
        @staticmethod
        def Redis(**kwargs):
            return StubRedis(**kwargs)

        @staticmethod
        def from_url(url):
            return StubRedis(url=url)

    monkeypatch.setattr(mq, "redis_lib", StubRedisLib)

    plugin = mq.RedisPubSubConnectorPlugin()
    conn = plugin.connect(host="localhost")
    env = plugin.fetch(conn, "topic")
    assert env.body == {"x": 1}
    plugin.send(conn, "topic", {"y": 2})
    assert conn["client"].published


def test_sqs_requires_dependency(monkeypatch):
    monkeypatch.setattr(mq, "boto3", None)
    plugin = mq.SQSPubSubConnectorPlugin()
    with pytest.raises(ImportError):
        plugin.connect(region_name="us-east-1")


def test_sqs_fetch_and_send_with_stubbed_boto3(monkeypatch):
    class StubSQS:
        def __init__(self):
            self.deleted = []
            self.sent = []

        def receive_message(self, **kwargs):
            return {
                "Messages": [
                    {
                        "MessageId": "mid",
                        "ReceiptHandle": "rh",
                        "Body": "{\"a\": 1}",
                        "Attributes": {},
                        "MessageAttributes": {},
                    }
                ]
            }

        def delete_message(self, QueueUrl, ReceiptHandle):
            self.deleted.append((QueueUrl, ReceiptHandle))

        def send_message(self, **kwargs):
            self.sent.append(kwargs)
            return {"MessageId": "m2"}

    class StubBoto3:
        @staticmethod
        def client(name, **kwargs):
            assert name == "sqs"
            return StubSQS()

    monkeypatch.setattr(mq, "boto3", StubBoto3)

    plugin = mq.SQSPubSubConnectorPlugin()
    conn = plugin.connect(region_name="us-east-1")
    envs = plugin.fetch(conn, "https://queue.url", max_messages=1)
    assert len(envs) == 1
    envs[0].ack_message()
    assert conn["client"].deleted

    out = plugin.send(conn, "https://queue.url", {"b": 2})
    assert out["success"] is True


def test_kafka_requires_dependency(monkeypatch):
    monkeypatch.setattr(mq, "KafkaConsumer", None)
    monkeypatch.setattr(mq, "KafkaProducer", None)
    plugin = mq.KafkaConnectorPlugin()
    with pytest.raises(ImportError):
        plugin.connect(bootstrap_servers="localhost:9092")


def test_kafka_fetch_and_send_with_stubbed_kafka(monkeypatch):
    class StubRecord:
        def __init__(self):
            self.value = b"{\"a\": 1}"
            self.topic = "t"
            self.partition = 0
            self.offset = 10
            self.key = None

    class StubConsumer:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.subscribed = []
            self.committed = 0

        def subscribe(self, topics):
            self.subscribed.extend(topics)

        def poll(self, timeout_ms=0, max_records=1):
            return {"tp": [StubRecord()]}

        def commit(self):
            self.committed += 1

    class StubFuture:
        def get(self, timeout=10.0):
            return SimpleNamespace(topic="t", partition=0, offset=11)

    class StubProducer:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.sent = []

        def send(self, topic, value=None, key=None):
            self.sent.append((topic, value, key))
            return StubFuture()

    monkeypatch.setattr(mq, "KafkaConsumer", StubConsumer)
    monkeypatch.setattr(mq, "KafkaProducer", StubProducer)

    plugin = mq.KafkaConnectorPlugin()
    conn = plugin.connect(bootstrap_servers="localhost:9092", group_id="g")

    env = plugin.fetch(conn, "t")
    assert env.body == {"a": 1}
    env.ack_message()
    assert conn["consumer"].committed == 1

    out = plugin.send(conn, "t", {"b": 2}, sync=True)
    assert out["success"] is True
    assert conn["producer"].sent
