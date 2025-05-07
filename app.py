import os
import json
import re
from log_setup import setup_logger
from message_dispatcher import SenderBuilder

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))

rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")

broker_type = os.getenv("BROKER_TYPE", "redis")
exchange_name = os.getenv("EXCHANGE_NAME", "audio_transcription_exchange")

sender_type = os.getenv("SENDER_TYPE", "api")
sender_host = os.getenv("SENDER_HOST", "rabbitmq")
sender_port = int(os.getenv("SENDER_PORT", 5672))
sender_url = os.getenv("SENDER_URL", "http://api-gateway/transcriptions")
sender_user = os.getenv("SENDER_USER", "guest")
sender_password = os.getenv("SENDER_PASSWORD", "guest")
sender_header = os.getenv("SENDER_HEADER", "{}")
try:
    sender_header = json.loads(sender_header)
except json.JSONDecodeError:
    sender_header = {}

logger = setup_logger()

queue_items = [
    value for key, value in os.environ.items()
    if re.match(r'^QUEUE_ITEM_\d+$', key)
]

# send_queue_items = [
#     value for key, value in os.environ.items()
#     if re.match(r'^SEND_QUEUE_ITEM_\d+$', key)
# ]

if not queue_items:
    raise ValueError("No queue items found in environment variables.")

ack_strategy = None  #glabal
sender = None

consumer_builder = SenderBuilder()
sender_builder = SenderBuilder()

broker = (
    consumer_builder.with_sender_type("broker").with_broker(
        "rabbitmq").with_host(rabbitmq_host)  # genellikle env üzerinden alınır
    .with_port(rabbitmq_port).with_user(rabbitmq_user).with_password(
        rabbitmq_password).with_target_queue_list(
            queue_items).with_exchange_name(exchange_name).build())

sender = None

if sender_type == "api":
    sender = (sender_builder.with_sender_type(sender_type).with_url(
        sender_url).with_headers(sender_header).build())
elif sender_type == "broker":
    sender = (
        sender_builder.with_sender_type("broker").with_broker(
            sender_host).with_host(
                sender_host)  # genellikle env üzerinden alınır
        .with_port(sender_port).with_user(sender_user).with_password(
            sender_password).with_exchange_name(exchange_name).build())


# Callback fonksiyonu
def process_message(ch, method, properties, body):
    try:
        message = body.decode("utf-8")
        logger.info(
            f"DB_CONSUMER: Received message: {message} for {broker_type}")

        if sender_type == "api":
            sender.send(message)
        else:
            sender.safe_publish(queue_items=queue_items,
                                exchange_name="result_exchange",
                                message=message)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        delivery_tag = getattr(method, "delivery_tag", None)
        if delivery_tag and hasattr(broker, "handle_ack"):
            broker.handle_ack(delivery_tag)


for queue_name in queue_items:
    broker.consume_configure(queue_name=queue_name,
                             exchange_name=exchange_name)

if len(queue_items) > 1:
    broker.start_consuming_multiple(queue_names=queue_items,
                                    callback=process_message)
else:
    broker.start_consuming(queue_name=queue_items[0], callback=process_message)
