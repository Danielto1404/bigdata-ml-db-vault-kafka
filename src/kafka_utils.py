import kafka
import pandas as pd

PREDICTIONS_TOPIC = "kafka-predictions"


def get_producer(kafka_host: str, kafka_port: str) -> kafka.KafkaProducer:
    return kafka.KafkaProducer(bootstrap_servers=f"{kafka_host}:{kafka_port}")


def get_consumer(kafka_host: str, kafka_port: str) -> kafka.KafkaConsumer:
    return kafka.KafkaConsumer(
        PREDICTIONS_TOPIC,
        bootstrap_servers=f"{kafka_host}:{kafka_port}",
        value_deserializer=lambda x: x.decode("utf-8"),
        fetch_max_wait_ms=300_000, # 5 minutes
        auto_offset_reset="earliest"
    )


def send_kafka_predictions(producer: kafka.KafkaProducer, df: pd.DataFrame):
    for _, row in df.iterrows():
        row = tuple(row.values)
        msg = ",".join(map(str, row)).encode("utf-8")
        producer.send(PREDICTIONS_TOPIC, msg)


def get_predictions_from_kafka(consumer: kafka.KafkaConsumer) -> list:
    predictions = []
    for msg in consumer:
        print(msg)
        predictions.append(msg.value.split(","))
    return predictions


__all__ = [
    "get_producer", 
    "get_consumer",
    "send_kafka_predictions",
    "get_predictions_from_kafka"
]
