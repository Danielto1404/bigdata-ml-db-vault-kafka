import greenplumpython as gp

from .constants import TWITTER_SENTIMENTS_PREDICTIONS


def read_table(db: gp.Database, table: str) -> gp.DataFrame:
    return gp.DataFrame.from_table(table, db=db)


def read_predictions(db: gp.Database) -> gp.DataFrame:
    return read_table(db, TWITTER_SENTIMENTS_PREDICTIONS)
