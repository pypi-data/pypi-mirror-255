from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, hamming_loss
from sklearn.multioutput import MultiOutputClassifier

from datasets.load_dataset import load_dataset
from transformation.mimlTOmi.binary_relevance import BinaryRelevanceTransformation

dataset_train = load_dataset("../datasets/miml_birds_random_80train.arff", delimiter="'")
dataset_test = load_dataset("../datasets/miml_birds_random_20test.arff", delimiter="'")

binary_relevance_train = BinaryRelevanceTransformation(dataset_train)
binary_relevance_test = BinaryRelevanceTransformation(dataset_test)

datasets_train = binary_relevance_train.transform_dataset()
datasets_test = binary_relevance_test.transform_dataset()

classifiers = []

for x in range(dataset_train.get_number_labels()):
    classifier = MultiOutputClassifier(RandomForestClassifier(random_state=27))
    print(datasets_train[x][1])
    classifier.fit(datasets_train[x][0], datasets_train[x][1])
    classifiers.append(classifier)

# Predicciones
y_preds = []
y_tests = []
for x in range(dataset_train.get_number_labels()):
    y_pred = classifiers[x].predict(datasets_test[x][0])
    y_preds.append(y_pred)
    y_tests.append(datasets_test[x][1])

# Evaluación del modelo
print("Reporte de clasificación:\n", classification_report(y_tests, y_preds, zero_division=0))

# print("Y TEST:",y_test)
# print("Y Pred:",y_pred)

print('Hamming Loss: ', round(hamming_loss(y_tests, y_preds), 2))
