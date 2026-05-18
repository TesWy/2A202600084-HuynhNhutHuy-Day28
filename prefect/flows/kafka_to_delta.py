# prefect/flows/kafka_to_delta.py
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from kafka import KafkaConsumer
from prefect import flow, task

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
DELTA_LAKE_PATH = os.environ.get("DELTA_LAKE_PATH", str(PROJECT_ROOT / "delta-lake" / "raw"))


@task
def consume_and_process():
    """Consume records from Kafka topic data.raw."""
    consumer = KafkaConsumer(
        "data.raw",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        consumer_timeout_ms=5000,
        value_deserializer=lambda m: json.loads(m.decode()),
    )
    records = [msg.value for msg in consumer]
    consumer.close()
    print(f"Consumed {len(records)} records from Kafka")
    return records


@task
def save_to_delta(records):
    """Simulate Delta Lake by writing parquet batches."""
    if not records:
        print("No records to save")
        return

    df = pd.DataFrame(records)
    os.makedirs(DELTA_LAKE_PATH, exist_ok=True)
    filename = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
    output_path = Path(DELTA_LAKE_PATH) / filename
    df.to_parquet(output_path)
    print(f"Saved {len(df)} records to {output_path}")


@flow(name="Kafka to Delta Pipeline")
def kafka_to_delta_flow():
    """Main flow: consume from Kafka and save to Delta Lake."""
    records = consume_and_process()
    save_to_delta(records)


if __name__ == "__main__":
    if os.environ.get("PREFECT_DEPLOY", "0") == "1":
        kafka_to_delta_flow.deploy(name="kafka-to-delta", work_pool_name="lab28-pool")
    else:
        kafka_to_delta_flow()
