import sys
import time
from sklearn.exceptions import ConvergenceWarning
from sklearn.utils import all_estimators
from sklearn.base import RegressorMixin, ClassifierMixin
import numpy as np


def train_model(reg, X_train, y_train, T, score, hide_warnings=True):
    try:
        model = reg()
    except Exception as e:
        if not hide_warnings:
            print(f"ERROR with {reg} at construction time: {e}")
        return

    try:
        training_time = 0
        st = time.time()
        while st + T > time.time():
            model.fit(X_train, y_train)
            training_time += 1
    except Exception as e:
        if not hide_warnings:
            print(f"ERROR with {model.__class__.__name__} at training time: {e}")
        return

    try:
        inference_time = 0
        st = time.time()
        while st + T > time.time():
            y = model.predict(X_train)
            inference_time += 1
    except Exception as e:
        score.append((model.__class__.__name__, training_time, "N/A"))
        if not hide_warnings:
            print(f"ERROR with {model.__class__.__name__} at inference time: {e}")
        return

    score.append((model.__class__.__name__, training_time, inference_time))


def bench(
        num_samples: int,
        num_features: int,
        fix_comp_time: float,
        hide_warning=True):
    if hide_warning == True:
        import warnings
        for warn in [DeprecationWarning, FutureWarning, UserWarning, RuntimeWarning, ConvergenceWarning]:
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            warnings.filterwarnings("ignore", category=FutureWarning)
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            warnings.filterwarnings("ignore", category=ConvergenceWarning)

    X_train = np.zeros((num_samples, num_features))
    y_train = np.ones((len(X_train),)) * 0.5

    score = []

    model_constructors = [est for est in all_estimators() if issubclass(est[1], RegressorMixin)]

    # Set the maximum allowed time for training in seconds
    for num_samples, model_constructor in model_constructors:
        train_model(model_constructor, X_train, y_train, fix_comp_time, score, hide_warning)

    score.sort(
        key=lambda x: x[1])  # x[0] -> sorting according algo name, x[1] according training time, x[2] inference time
    for s in score:
        print(' '.join(map(str, s)))


if __name__ == "__main__":
    bench(num_samples=1000, num_features=100, fix_comp_time=60)
