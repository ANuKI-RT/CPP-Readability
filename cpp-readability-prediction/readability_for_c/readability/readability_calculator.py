import pickle
import random
from pathlib import Path
from typing import List, Tuple

import numpy as np

from metrics import factory
from readability.model import Model


class ReadabilityCalculator:
    def compute_readability(self, source_code: str) -> Tuple[int, float]:
        raise NotImplemented()


class DummyReadabilityCalculator(ReadabilityCalculator):
    def compute_readability(self, source_code: str) -> Tuple[int, float]:
        prob = random.random()
        return round(prob), prob


class PickleReadabilityCalculator(ReadabilityCalculator):
    def __init__(self, path: Path, language: str = 'cpp'):
        self.path = path
        self.language = language
        self.loaded: Model = self.load_model(path)

    @staticmethod
    def load_model(path: Path) -> Model:
        with path.open('rb') as infile:
            return pickle.load(infile)

    def predict(self, metrics_values: List[float]) -> Tuple[int, float]:
        result = self.loaded.pipeline.predict_proba(np.array([metrics_values]))
        return int(result[0][0]), float(result[0][1])

    def compute_readability(self, source_code: str) -> Tuple[int, float]:
        metric_values = []
        feature_calculators = factory.get_all_feature_calculators(source_code, self.language)
        feature_names = self.loaded.pipeline.feature_names_in_.tolist()
        for name in feature_names:
            metric_values.append(feature_calculators[name].calculate_metric())
        return self.predict(metric_values)
