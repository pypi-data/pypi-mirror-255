from datasets.load_dataset import load_dataset

dataset = load_dataset("../datasets/toy.csv")

dataset.show_bag("bag2")

dataset.add_instance("bag2", [12, 22, 13])

dataset.show_bag("bag2")

# TODO: Añadir ejemplo de set_attribute, add_attribute y add_bag

dataset.describe()
