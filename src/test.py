import argparse
import configparser
import logging

import numpy as np
import pandas as pd

import db as db_tools
import kafka_utils
from train import TweetsClassificationTrainer
from vault import HashicorpVault

config = configparser.ConfigParser()
config.read("config.ini")


def main():
    logging.info("Launching functional test")
    parser = argparse.ArgumentParser("Twitter sentiment testing")
    parser.add_argument("--data", default="tests/samples.csv")
    parser.add_argument("--model", default="experiments/tfidf_logreg/model.pkl")
    parser.add_argument("--vault-token", required=True)

    args = parser.parse_args()

    trainer = TweetsClassificationTrainer.from_pretrained(args.model)
    test_data = pd.read_csv(args.data, encoding=config["data"]["encoding"])
    predictions = trainer.predict(test_data)

    if not np.all(predictions == test_data.Sentiment.values):
        logging.error("Functional test: Failed")
        return
    else:
        logging.info("Functional test: Passed")

    vault = HashicorpVault(args.vault_token)
    db_credentials = vault.read_postgres_credentials()
    kafka_credentials = vault.read_kafka_credentials()

    params = dict(
        user=db_credentials.user,
        password=db_credentials.password,
        dbname=db_credentials.dbname,
        host=db_tools.POSTGRES_HOST,
        port=db_tools.POSTGRES_PORT,
    )

    db = db_tools.get_db(**params)

    test_data["login"] = params["user"]
    test_data["prediction"] = predictions

    logging.info("Writing predictions to database")
    test_data = db_tools.write_predictions(db, test_data)

    logging.info("Reading predictions from database")
    predictions_from_db = db_tools.read_predictions(db)
    print(predictions_from_db[:5])

    producer = kafka_utils.get_producer(
        kafka_host=kafka_credentials.host,
        kafka_port=kafka_credentials.port
    )

    consumer = kafka_utils.get_consumer(
        kafka_host=kafka_credentials.host,
        kafka_port=kafka_credentials.port
    )

    logging.info("Sending predictions to Kafka")
    kafka_utils.send_kafka_predictions(producer, test_data)
    
    logging.info("Reading predictions from Kafka")
    predictions_from_kafka = kafka_utils.get_predictions_from_kafka(consumer)
    logging.info("Predictions from Kafka")
    logging.info(predictions_from_kafka[:5])


if __name__ == "__main__":
    main()
