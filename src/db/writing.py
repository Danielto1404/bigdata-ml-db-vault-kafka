import io

import pandas as pd

from .constants import TWITTER_SENTIMENTS_PREDICTIONS
from .database import Database


def write_predictions(db: Database, predictions: pd.DataFrame):
    predictions = predictions.rename(columns={
        "ItemID": "item_id",
        "Sentiment": "target",
        "SentimentText": "text"
    })

    stream = io.StringIO()
    predictions = predictions[["login", "item_id", "text", "target", "prediction"]]
    predictions.to_csv(stream, sep="\t", header=False, index=False)
    stream.seek(0)

    cursor = db.conn.cursor()
    cursor.copy_from(stream, TWITTER_SENTIMENTS_PREDICTIONS)


__all__ = ["write_predictions"]