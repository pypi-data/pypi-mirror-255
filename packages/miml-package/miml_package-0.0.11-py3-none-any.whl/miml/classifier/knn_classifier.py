from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier

import classifier.abstract_classifier


class KNNClassifier(classifier.abstract_classifier.AbstractClassifier):

    def __init__(self, k=3):
        self.k = k
        self.model = None

    def train(self, training_data, training_labels):
        self.model = KNeighborsClassifier(n_neighbors=self.k)
        self.model.fit(training_data, training_labels)

    def predict(self, test_data):
        return self.model.predict(test_data)

    def evaluate(self, test_data, test_labels):
        predictions = self.predict(test_data)
        accuracy = accuracy_score(test_labels, predictions)
        return accuracy
