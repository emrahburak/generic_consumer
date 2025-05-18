import os
import json
import re
from message_bridge import setup_logger
from message_bridge import SenderBuilder


prefix = "GENERIC_"

generic_host_type = os.getenv(f"{prefix}HOST_TYPE")
generic_host = os.getenv(f"{prefix}HOST")
generic_port = int(os.getenv(f"{prefix}PORT",6379))
generic_user = os.getenv(f"{prefix}USER")
generic_password = os.getenv(f"{prefix}PASSWORD")


publisher_exchange = os.getenv(f"{prefix}PUBLISHER_EXCHANGE_NAME")
consumer_exchange = os.getenv(f"{prefix}CONSUMER_EXCHANGE_NAME")



sender_type = os.getenv(f"{prefix}SENDER_TYPE")
sender_host = os.getenv(f"{prefix}SENDER_HOST")
sender_port = int(os.getenv(f"{prefix}SENDER_PORT", 5672))
sender_url = os.getenv(f"{prefix}SENDER_URL")
sender_user = os.getenv(f"{prefix}SENDER_USER", "guest")
sender_password = os.getenv(f"{prefix}SENDER_PASSWORD", "guest")
sender_header = os.getenv(f"{prefix}SENDER_HEADER", "{}")





try:
    sender_header = json.loads(sender_header)
except json.JSONDecodeError:
    sender_header = {}

logger = setup_logger()

pattern = re.compile(rf"^{prefix}CONSUMER_QUEUE_ITEM_\d+$")

consumer_queue_items = [
    value for key, value in os.environ.items()
    if pattern.match(key)
]

if not consumer_queue_items:
    raise ValueError("No queue items found in environment variables.")


pattern_publisher = re.compile(rf"^{prefix}PUBLISHER_QUEUE_ITEM_\d+$")

publisher_queue_items = [
    value for key, value in os.environ.items()
    if pattern_publisher.match(key)
]

if not publisher_queue_items:
    raise ValueError("No queue items found in environment variables.")



consumer_builder = SenderBuilder()
sender_builder = SenderBuilder()

consumer = (
    consumer_builder.with_sender_type(generic_host_type).with_broker(
        generic_host).with_host(generic_host)  # genellikle env üzerinden alınır
    .with_port(generic_port).with_user(generic_user).with_password(
        generic_password).with_target_queue_list(
            consumer_queue_items).with_exchange_name(consumer_exchange).build())


if sender_type == "api":
    sender = (sender_builder.with_sender_type(sender_type).with_url(
        sender_url).with_headers(sender_header).build())
elif sender_type == "broker":
    sender = (
        sender_builder.with_sender_type(sender_type).with_broker(
            sender_host).with_host(
                sender_host)  # genellikle env üzerinden alınır
        .with_port(sender_port).with_user(sender_user).with_password(
            sender_password).with_exchange_name(publisher_exchange).build())


# Callback fonksiyonu
def process_message(ch, method, properties, body):
    try:
        message = body.decode("utf-8")
        logger.info(
            f"DB_CONSUMER: Received message: {message} for {generic_host}")

        if sender_type == "api":
            sender.send(message)
        else:
            sender.safe_publish(queue_items=publisher_queue_items,
                                exchange_name=publisher_exchange,
                                message=message)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        delivery_tag = getattr(method, "delivery_tag", None)
        if delivery_tag and hasattr(consumer, "handle_ack"):
            consumer.handle_ack(delivery_tag)


for queue_name in consumer_queue_items:
    consumer.configure(queue_name=queue_name,
                             exchange_name=consumer_exchange)

if len(consumer_queue_items) > 1:
    consumer.start_consuming_multiple(queue_names=consumer_queue_items,
                                    callback=process_message)
else:
    consumer.start_consuming(queue_name=consumer_queue_items[0], callback=process_message)
