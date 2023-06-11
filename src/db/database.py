import greenplumpython as gp


class Database(gp.Database):
    def __init__(self, params: dict):
        super().__init__(params=params)
        self.conn = self._conn  # Make connection available for testing


def get_db(user: str, password: str, host: str, port: str, dbname: str) -> Database:
    params = dict(
        user=user,
        password=password,
        host=host,
        port=port,
        dbname=dbname
    )
    return Database(params=params)


__all__ = ["get_db", "Database"]
