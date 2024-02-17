import numpy as np
from tabulate import tabulate


class Instance:

    def __init__(self, values, attributes: dict = None):
        self.dataset = None
        self.data = np.array(values)
        # Estructura que almacene la informacion de los atributos(nombre, si es label, etc)
        # TODO: Ver si crear clase
        self.attributes = attributes

    def get_number_attributes(self):
        return len(self.attributes)

    def get_number_classes(self):
        cont = 0
        for x in self.attributes:
            if self.attributes[x] == 1:
                cont += 1
        return cont

    def get_attribute_by_index(self, index: int):
        return self.data.item(index)

    def get_attribute_by_name(self, attribute: str):
        index = list(self.attributes.keys()).index(attribute)
        return self.data.item(index)

    def set_attribute_by_index(self, index: int, value):
        self.data[index] = value

    def set_attribute_by_name(self, attribute: str, value):
        index = list(self.attributes.keys()).index(attribute)
        self.data[index] = value

    def set_dataset(self, dataset):
        self.dataset = dataset

    def add_attribute(self, name, position=0, value=0):
        if position is None:
            position = len(self.data)
        # TODO: Habria que ordenar el diccionario para poder poner el atributo en la posicion que se quiera
        self.attributes.insert(position, name)
        self.data = np.insert(self.data, position, value)

    def delete_attribute(self, position):
        pass

    def delete_attribute(self, name):
        pass

    def show_instance(self):
        # TODO: Check

        table = []

        table.append(list(self.data))

        # table = [['col 1', 'col 2', 'col 3', 'col 4'], [1, 2222, 30, 500], [4, 55, 6777, 1]]
        # print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
        # print(tabulate([key], tablefmt="grid"))
        print(tabulate(table, tablefmt="grid", numalign="center"))
