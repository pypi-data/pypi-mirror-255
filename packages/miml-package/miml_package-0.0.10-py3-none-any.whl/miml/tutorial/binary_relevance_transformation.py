from sklearn.metrics import classification_report, hamming_loss

from classifier.knn_classifier import KNNClassifier
from datasets.load_dataset import load_dataset
from transformation.mimlTOmi.binary_relevance import BinaryRelevanceTransformation

dataset_train = load_dataset("../datasets/miml_birds_random_80train.arff", delimiter="'")
dataset_test = load_dataset("../datasets/miml_birds_random_20test.arff", delimiter="'")

binary_relevance_train = BinaryRelevanceTransformation(dataset_train)
binary_relevance_test = BinaryRelevanceTransformation(dataset_test)

datasets_train = binary_relevance_train.transform_dataset()
datasets_test = binary_relevance_test.transform_dataset()

classifiers = []

for i in range(len(datasets_train)):
    knn_classifier = KNNClassifier(k=5)
    print("Train attrib: ", datasets_train[i][0])
    print("Train labels: ", datasets_train[i][1])
    knn_classifier.train(datasets_train[i][0], datasets_train[i][1])
    classifiers.append(knn_classifier)

y_preds = []
y_tests = []
for i in range(dataset_train.get_number_labels()):
    y_pred = []
    for j in range(len(datasets_train[i][0])):
        y_pred.append(classifiers[i].predict(datasets_test[i][0][j]))
    y_preds.append(y_pred)
    y_tests.append(datasets_test[i][1])

# Evaluación del modelo
print("Reporte de clasificación:\n", classification_report(y_tests, y_preds, zero_division=0))

# print("Y TEST:",y_test)
# print("Y Pred:",y_pred)

print('Hamming Loss: ', round(hamming_loss(y_tests, y_preds), 2))
