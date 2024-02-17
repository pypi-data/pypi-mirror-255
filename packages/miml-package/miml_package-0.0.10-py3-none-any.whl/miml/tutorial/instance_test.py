from data.bag import Bag
from data.instance import Instance
from data.miml_dataset import MIMLDataset

values = [2, 7, 5.09, 1]
attr = {"hola1": 0, "hola2": 0, "hola3": 0, "label": 1}
instance1 = Instance(values, attr)
instance2 = Instance(values, attr)
instance3 = Instance(values, attr)
# print(instance1.data)
# instance1.show_instance()
bag = Bag(instance1, "bag1")
bag.add_instance(instance2)
bag.add_instance(instance3)

dataset = MIMLDataset()
dataset.add_bag(bag)
dataset.show_dataset()
