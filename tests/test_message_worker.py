import threading

import apilinker.core.message_queue as mq
from apilinker.core.error_handling import DeadLetterQueue


class SeqConsumer:
    def __init__(self, results):
        self._results = list(results)

    def fetch(self, connection, endpoint, **kwargs):
        if not self._results:
            return None
        return self._results.pop(0)


class FlakyProducer:
    def __init__(self, fail_times=0):
        self.fail_times = fail_times
        self.calls = 0
        self.sent = []

    def send(self, connection, endpoint, data, **kwargs):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RuntimeError("send failed")
        self.sent.append((endpoint, data))
        return {"success": True}


def test_worker_processes_and_acks(tmp_path):
    acked = {"n": 0}

    def ack():
        acked["n"] += 1

    env = mq.MessageEnvelope(body={"x": 1}, source="in", ack=ack)

    consumer = SeqConsumer([env, None])
    producer = FlakyProducer(fail_times=0)

    pipeline = mq.MessagePipeline(
        consumer=consumer,
        producer=producer,
        dlq=DeadLetterQueue(str(tmp_path / "dlq")),
    )

    worker = mq.MessageWorker(
        pipeline,
        consumer_connection={},
        producer_connection={},
        source="in",
        default_destination="out",
    )

    result = worker.run(max_loops=2)

    assert result["processed"] == 1
    assert result["sent"] == 1
    assert result["failed"] == 0
    assert producer.sent == [("out", {"x": 1})]
    assert acked["n"] == 1


def test_worker_retries_and_succeeds(monkeypatch, tmp_path):
    monkeypatch.setattr(mq.time, "sleep", lambda _: None)

    env = mq.MessageEnvelope(body={"x": 1}, source="in")
    consumer = SeqConsumer([env])
    producer = FlakyProducer(fail_times=1)

    pipeline = mq.MessagePipeline(
        consumer=consumer,
        producer=producer,
        dlq=DeadLetterQueue(str(tmp_path / "dlq")),
    )

    worker = mq.MessageWorker(
        pipeline,
        consumer_connection={},
        producer_connection={},
        source="in",
        default_destination="out",
        retry_policy=mq.RetryPolicy(
            max_attempts=2,
            initial_delay_seconds=0.0,
            max_delay_seconds=0.0,
            backoff_multiplier=1.0,
            jitter_seconds=0.0,
        ),
    )

    result = worker.run(max_loops=1)

    assert result["processed"] == 1
    assert result["sent"] == 1
    assert result["failed"] == 0
    assert producer.calls == 2


def test_worker_writes_dlq_after_retry_exhaustion(monkeypatch, tmp_path):
    monkeypatch.setattr(mq.time, "sleep", lambda _: None)

    nacked = {"n": 0}

    def nack(requeue=False):
        nacked["n"] += 1

    dlq_dir = tmp_path / "dlq"

    env = mq.MessageEnvelope(body={"x": 1}, source="in", nack=nack)
    consumer = SeqConsumer([env])
    producer = FlakyProducer(fail_times=10)

    pipeline = mq.MessagePipeline(
        consumer=consumer,
        producer=producer,
        dlq=DeadLetterQueue(str(dlq_dir)),
    )

    worker = mq.MessageWorker(
        pipeline,
        consumer_connection={},
        producer_connection={},
        source="in",
        default_destination="out",
        retry_policy=mq.RetryPolicy(
            max_attempts=2,
            initial_delay_seconds=0.0,
            max_delay_seconds=0.0,
            backoff_multiplier=1.0,
            jitter_seconds=0.0,
        ),
    )

    result = worker.run(max_loops=1)

    assert result["processed"] == 1
    assert result["sent"] == 0
    assert result["failed"] == 1
    assert result["dlq_written"] == 1
    assert nacked["n"] == 1
    assert list(dlq_dir.glob("*.json"))


def test_worker_idle_backoff(monkeypatch, tmp_path):
    sleeps = []

    def fake_sleep(secs):
        sleeps.append(secs)

    monkeypatch.setattr(mq.time, "sleep", fake_sleep)

    consumer = SeqConsumer([None, None, None])
    producer = FlakyProducer(fail_times=0)

    pipeline = mq.MessagePipeline(
        consumer=consumer,
        producer=producer,
        dlq=DeadLetterQueue(str(tmp_path / "dlq")),
    )

    worker = mq.MessageWorker(
        pipeline,
        consumer_connection={},
        producer_connection={},
        source="in",
        default_destination="out",
        idle_backoff=mq.IdleBackoffPolicy(
            initial_sleep_seconds=0.01,
            max_sleep_seconds=1.0,
            backoff_multiplier=2.0,
        ),
        stop_event=threading.Event(),
    )

    result = worker.run(max_loops=3)

    assert result["processed"] == 0
    assert result["sent"] == 0
    assert result["failed"] == 0
    assert len(sleeps) == 3
    assert sleeps[0] == 0.01
    assert sleeps[1] == 0.02
    assert sleeps[2] == 0.04
