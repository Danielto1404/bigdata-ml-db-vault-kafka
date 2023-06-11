import argparse
import configparser
import logging
import os
import pickle
import sys
import typing as tp

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import constants
from preprocess import clean_text, split_for_validation

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

config = configparser.ConfigParser()
config.read("config.ini")


class TweetsClassificationTrainer:
    """
    Trainer for Tweets Classification

    Simple example of how to use this class:
    ```
    trainer = TweetsClassificationTrainer.default_trainer(train_path, test_path)
    train_f1, val_f1 = trainer.fit(with_validation=True)
    test_predictions = trainer.predict(trainer.get_test())
    trainer.save_model(model_save_path)
    ```
    """

    def __init__(self, model, train_path: tp.Optional[str] = None, test_path: tp.Optional[str] = None):
        self.model = model
        self.train_path = train_path
        self.test_path = test_path

    def get_train_data(self) -> pd.DataFrame:
        """Returns train data as pandas DataFrame
        """
        return pd.read_csv(self.train_path, encoding=config["data"]["encoding"])

    def get_test_data(self) -> pd.DataFrame:
        """Returns test data as pandas DataFrame"""
        return pd.read_csv(self.test_path, encoding=config["data"]["encoding"])

    def fit(self, use_validation: bool = False) -> (float, float):
        """
        Fits model on train data
        :param use_validation: bool - whether to use validation data
        :return: train_f1, val_f1 - f1 scores for train and validation data
        """
        train_df = self.get_train_data()
        x_train, y_train = train_df[constants.TEXT_COLUMN], train_df[constants.LABEL_COLUMN]
        x_train = x_train.apply(clean_text)

        if use_validation:
            x_train, x_val, y_train, y_val = split_for_validation(train_df)
            self.model.fit(x_train, y_train)
            train_f1 = self.evaluate(x_train, y_train)
            val_f1 = self.evaluate(x_val, y_val)
            return train_f1, val_f1
        else:
            self.model.fit(x_train, y_train)
            train_f1 = self.evaluate(x_train, y_train)
            return train_f1, None

    def evaluate(self, x: pd.Series, y: pd.Series) -> float:
        """
        Evaluates model on x and y
        :param x: Series - x data
        :param y: Series - y data
        :return: macro f1 score
        """
        x = x.apply(clean_text)
        y_pred = self.model.predict(x)
        return f1_score(y, y_pred, average="macro")

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """
        Predicts on data
        :param data: DataFrame - data to predict on
        :return: DataFrame - predictions
        """
        data = data[constants.TEXT_COLUMN].apply(clean_text)
        return self.model.predict(data)

    def save_model(self, model_save_path: str):
        """Saves model to model_save_path"""
        with open(model_save_path, "wb") as f:
            pickle.dump(self.model, f)

    @staticmethod
    def from_pretrained(model_path: str) -> "TweetsClassificationTrainer":
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        return TweetsClassificationTrainer(model)

    @staticmethod
    def default_trainer(train_path: str, test_path: str) -> "TweetsClassificationTrainer":
        """Returns default trainer for Tweets Classification"""
        model = Pipeline([
            ("tfidf", TfidfVectorizer(
                stop_words=config["model.tfidf.hyperparams"]["stop_words"].split(","),
                lowercase=bool(config["model.tfidf.hyperparams"]["lowercase"]),
                max_features=int(config["model.tfidf.hyperparams"]["max_features"]),
                ngram_range=(int(config["model.tfidf.hyperparams"]["ngram_range_min"]),
                             int(config["model.tfidf.hyperparams"]["ngram_range_max"])),
            )),
            ("scaler", StandardScaler(with_mean=False)),
            ("logreg", LogisticRegression(
                C=float(config["model.logreg.hyperparams"]["C"]),
                solver=config["model.logreg.hyperparams"]["solver"],
                max_iter=int(config["model.logreg.hyperparams"]["max_iter"])
            ))
        ])

        return TweetsClassificationTrainer(model, train_path, test_path)


def main():
    parser = argparse.ArgumentParser(prog="Tweets Classification Trainer")
    parser.add_argument("--train", default="data/train.csv")
    parser.add_argument("--test", default="data/test.csv")
    parser.add_argument("--exp_name", required=True)
    args = parser.parse_args()

    trainer = TweetsClassificationTrainer.default_trainer(args.train, args.test)
    logging.info("Fitting model")
    train_f1, valid_f1 = trainer.fit(use_validation=True)

    logging.info(f"Train F1 {train_f1} | Valid F1 {valid_f1}")

    os.makedirs(f"experiments/{args.exp_name}", exist_ok=True)
    model_save_path = f"experiments/{args.exp_name}/model.pkl"
    test_preds_path = f"experiments/{args.exp_name}/test_preds.csv"

    logging.info("Predicting on test data")
    test_df = trainer.get_test_data()
    labels = trainer.predict(test_df.iloc[:100])
    logging.info("Saving test predictions")
    pd.DataFrame({"label": labels}).to_csv(test_preds_path, header=True, index=False)

    trainer.save_model(model_save_path)


if __name__ == "__main__":
    main()
