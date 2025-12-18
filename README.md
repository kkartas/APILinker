# ApiLinker

[![PyPI version](https://badge.fury.io/py/apilinker.svg)](https://badge.fury.io/py/apilinker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kkartas/APILinker/HEAD?labpath=examples%2FApiLinker_Research_Tutorial.ipynb)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://kkartas.github.io/APILinker/)

**A universal bridge to connect, map, and automate data transfer between any two REST APIs.**

---

## 📚 Documentation

Full documentation is available at **[https://kkartas.github.io/APILinker/](https://kkartas.github.io/APILinker/)**.

## 🚀 Quick Install

```bash
pip install apilinker
```

## ⭐ Message Queue Connectors

Message-queue connectors are optional.

```bash
pip install apilinker[mq]
```

Minimal example (worker loop):

```python
from apilinker.core.error_handling import DeadLetterQueue
from apilinker.core.message_queue import MessagePipeline, MessageWorker
from apilinker.core.message_queue_connectors import RabbitMQConnectorPlugin

consumer = RabbitMQConnectorPlugin()
producer = RabbitMQConnectorPlugin()

consumer_conn = consumer.connect(host="localhost")
producer_conn = producer.connect(host="localhost")

pipeline = MessagePipeline(
    consumer=consumer,
    producer=producer,
    dlq=DeadLetterQueue("./dlq"),
)

worker = MessageWorker(
    pipeline,
    consumer_connection=consumer_conn,
    producer_connection=producer_conn,
    source="input_queue",
    default_destination="output_queue",
)

worker.run()
```

## 🌟 Features

- 🔄 **Universal Connectivity** - Connect any two REST APIs.
- 🗺️ **Powerful Mapping** - Transform data with ease.
- ⭐ **Event-Driven Pipelines** - Optional message queue connectors (RabbitMQ, Redis Pub/Sub, AWS SQS, Kafka).
- 🔒 **Secure** - Enterprise secret management (Vault, AWS, Azure, GCP).
- 🧬 **Scientific Connectors** - Built-in support for NCBI, arXiv, and more.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/developer-guide/contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
