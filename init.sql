CREATE TABLE twitter_sentiment_predictions
(
    login      VARCHAR(255) NOT NULL,
    item_id    INT          NOT NULL PRIMARY KEY,
    text       TEXT         NOT NULL,
    target     INT          NOT NULL,
    prediction INT          NOT NULL
);