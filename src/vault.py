import argparse
import dataclasses
import logging

import hvac

HASHICORP_VAULT_HOST = "vault"
HASHICORP_VAULT_PORT = 8200


@dataclasses.dataclass
class PostgresCredentials:
    user: str
    password: str
    dbname: str


@dataclasses.dataclass
class KafkaCredentials:
    host: str
    port: str


class HashicorpVault:
    POSTGRES_CREDENTIALS_PATH = "postgres/credentials"
    KAFKA_CREDENTIALS_PATH = "kafka/credentials"

    def __init__(self, token: str):
        url = f"http://{HASHICORP_VAULT_HOST}:{HASHICORP_VAULT_PORT}"
        self.client = hvac.Client(url=url, token=token)

    def read_postgres_credentials(self) -> PostgresCredentials:
        secrets = self.client.secrets.kv.v2.read_secret_version(
            path=self.POSTGRES_CREDENTIALS_PATH
        )
        return PostgresCredentials(**secrets["data"]["data"])

    def store_postgres_credentials(self, user: str, password: str, dbname: str):
        self.client.secrets.kv.v2.create_or_update_secret(
            path=self.POSTGRES_CREDENTIALS_PATH,
            secret=dict(user=user, password=password, dbname=dbname)
        )

    def read_kafka_credentials(self) -> KafkaCredentials:
        secrets = self.client.secrets.kv.v2.read_secret_version(
            path=self.KAFKA_CREDENTIALS_PATH
        )
        return KafkaCredentials(**secrets["data"]["data"])

    def store_kafka_credentials(self, host: str, port: str):
        self.client.secrets.kv.v2.create_or_update_secret(
            path=self.KAFKA_CREDENTIALS_PATH,
            secret=dict(host=host, port=port)
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Hashicorp Vault CLI")
    parser.add_argument("--token", required=True)
    parser.add_argument("--postgres-user", required=True)
    parser.add_argument("--postgres-password", required=True)
    parser.add_argument("--postgres-dbname", required=True)
    parser.add_argument("--kafka-host", required=True)
    parser.add_argument("--kafka-port", required=True)

    args = parser.parse_args()

    vault = HashicorpVault(token=args.token)

    vault.store_postgres_credentials(
        user=args.postgres_user,
        password=args.postgres_password,
        dbname=args.postgres_dbname
    )

    vault.store_kafka_credentials(
        host=args.kafka_host,
        port=args.kafka_port
    )

    logging.info("Credentials stored")
