# scripts/01_ingest_to_kafka.py
import json
import os
import time

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "data.raw")

sample_data = [
    {"id": "doc_001", "text": "AI platform integration test", "timestamp": time.time()},
    {"id": "doc_002", "text": "Kafka to Prefect pipeline", "timestamp": time.time()},
]


def ensure_topic() -> None:
    admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS, client_id="lab28-admin")
    try:
        admin.create_topics([NewTopic(name=TOPIC, num_partitions=1, replication_factor=1)])
    except TopicAlreadyExistsError:
        pass
    finally:
        admin.close()


def ingest_data(records: list[dict]) -> None:
    ensure_topic()
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    for record in records:
        producer.send(TOPIC, value=record)
        print(f"Sent: {record['id']}")
    producer.flush()
    producer.close()


if __name__ == "__main__":
    ingest_data(sample_data)
    print(f"Integration 1 OK: Data -> Kafka topic {TOPIC}")
