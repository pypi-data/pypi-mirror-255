class Node:
    min_depth = 1
    selection_probability = 0.2
    n_inputs = 0
    edges = 0

    def __init__(self):
        pass

    @property
    def depth(self):
        pass

    @property
    def size(self):
        return

    def sanitise(self,parent_conditions:list=[])->object:
        pass

    def find(self, target_index: int, current_index: int, replace: object=None) -> (int, object):
        pass

    def resolve(self, data):
        pass

    def resolve_ga_fitness(self, data):
        pass

    def to_database_switch_case(self) -> list:
        pass

    def compile(self) -> str:
        pass

    def to_function(self, indent:int=0) -> str:
        pass

    def get_data_fields(self) -> set:
        pass

