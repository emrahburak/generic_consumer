# Generic Consumer

**Generic Consumer** is a flexible and lightweight message broker consumer that can receive messages from a queue (e.g. Redis, RabbitMQ) and, based on configuration, either:

- POST the message to an HTTP API, or
- re-publish it to another message broker queue.

It is designed to be modular, easily extendable, and works well in pipeline or microservice environments.

---

## ✨ Features

- ✅ Redis and RabbitMQ support (plug-and-play design)
- 🔁 Forward messages to:
  - RESTful HTTP endpoints
  - Another message queue (fan-out or routing)
- 🧩 Builder-pattern-based configuration
- 📦 Easy to embed in larger systems or use standalone

---

## 🚀 Getting Started

### Installation

Clone the repo:

```bash
git clone https://github.com/emrahburak/generic_consumer

or 

git clone https://gitlab.com/EmrahBurak/generic_consumer.git

cd generic_consumer

