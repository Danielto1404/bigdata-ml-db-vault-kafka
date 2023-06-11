import dataclasses
import logging

import hvac
import argparse

HASHICORP_VAULT_HOST = "vault"
HASHICORP_VAULT_PORT = 8200


@dataclasses.dataclass
class PostgresCredentials:
    user: str
    password: str
    dbname: str


class HashicorpVault:
    POSTGRES_CREDENTIALS_PATH = "postgres/credentials"

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Hashicorp Vault CLI")
    parser.add_argument("--token", required=True)
    parser.add_argument("--postgres-user", required=True)
    parser.add_argument("--postgres-password", required=True)
    parser.add_argument("--postgres-dbname", required=True)

    args = parser.parse_args()

    vault = HashicorpVault(token=args.token)
    vault.store_postgres_credentials(
        user=args.postgres_user,
        password=args.postgres_password,
        dbname=args.postgres_dbname
    )

    logging.info("Credentials stored")
