import kafka
import pandas as pd

PREDICTIONS_TOPIC = "kafka-predictions"


def get_producer(kafka_host: str, kafka_port: str) -> kafka.KafkaProducer:
    return kafka.KafkaProducer(bootstrap_servers=f"{kafka_host}:{kafka_port}")


def send_kafka_predictions(producer: kafka.KafkaProducer, df: pd.DataFrame):
    for _, row in df.iterrows():
        row = tuple(row.values)
        msg = ",".join(map(str, row)).encode("utf-8")
        producer.send(PREDICTIONS_TOPIC, msg)


__all__ = ["get_producer", "send_kafka_predictions"]
