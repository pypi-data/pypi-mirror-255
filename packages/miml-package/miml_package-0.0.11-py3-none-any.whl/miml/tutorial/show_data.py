from datasets.load_dataset import load_dataset

dataset = load_dataset("../datasets/miml_birds.csv")

dataset.show_dataset()

# print(dataset.get_instance("4", 1))

dataset.describe()
