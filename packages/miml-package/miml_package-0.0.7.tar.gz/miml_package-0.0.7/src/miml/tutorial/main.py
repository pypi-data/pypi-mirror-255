from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, hamming_loss
from sklearn.multioutput import MultiOutputClassifier

from datasets import load_dataset
from transformation.mimlTOml.arithmetic import ArithmeticTransformation

dataset_train = load_dataset("../datasets/miml_birds_random_80train.arff", delimiter="'")
dataset_test = load_dataset("../datasets/miml_birds_random_20test.arff", delimiter="'")

arithmetic_transformation_train = ArithmeticTransformation(dataset_train)
arithmetic_transformation_test = ArithmeticTransformation(dataset_test)

X_train, y_train = arithmetic_transformation_train.transform_dataset()
X_test, y_test = arithmetic_transformation_test.transform_dataset()

classifier = MultiOutputClassifier(RandomForestClassifier(random_state=27))
classifier.fit(X_train, y_train)

# Predicciones
y_pred = classifier.predict(X_test)

# Evaluación del modelo
print("Reporte de clasificación:\n", classification_report(y_test, y_pred, zero_division=0))

# print("Y TEST:",y_test)
# print("Y Pred:",y_pred)

print('Hamming Loss: ', round(hamming_loss(y_test, y_pred), 2))
