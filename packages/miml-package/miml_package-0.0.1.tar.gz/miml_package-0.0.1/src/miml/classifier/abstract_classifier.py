from abc import ABC, abstractmethod


class AbstractClassifier(ABC):

    @abstractmethod
    def train(self, training_data, training_labels):
        pass

    @abstractmethod
    def predict(self, test_data):
        pass

    @abstractmethod
    def evaluate(self, test_data, test_labels):
        pass
