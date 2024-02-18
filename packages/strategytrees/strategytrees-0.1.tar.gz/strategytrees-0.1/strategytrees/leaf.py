from .node import Node
import random

class Leaf(Node):
    _value:str = None
    selection_probability = 0.5

    def __init__(self, value:str):
        self._value = value

    def get_data_fields(self) -> list:
        return []

    @property
    def value(self):
        return self._value

    @property
    def depth(self)->int:
        return 1

    @property
    def size(self)->int:
        return 1

    def __str__(self):
        return self._value

    def sanitise(self, parent_conditions:list=[])->Node:
        return self

    def find(self, target_index, current_index, replace:Node=None):
        return current_index, None

    def compile(self)->str:
        return f"st.Leaf('{self._value}')"

    def resolve(self, data) -> str:
        """

        :param data:
        :return:
        """
        return self._value

    def resolve_ga_fitness(self, data) -> Node:
        return self._value

    def to_function(self, indent:int=0) -> str:
        t = '\t'
        return f"{t*indent}return '{self._value}'\n"
