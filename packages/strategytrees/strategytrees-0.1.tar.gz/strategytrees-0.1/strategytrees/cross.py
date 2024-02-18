from .node import Node
from .leaf import Leaf

class Cross(Node):
    min_depth = 2
    selection_probability = 0.1
    n_inputs = 2
    edges = 3

    condition_up:Node = None
    condition_down:Node = None
    condition_false:Node = None
    def __init__(self,
                 previous_field_a:str,
                 current_field_a,
                 field_b:str,
                 condition_up:Node,
                 condition_down:Node,
                 condition_false:Node):
        self.previous_field_a = previous_field_a
        self.current_field_a = current_field_a
        self.field_b = field_b
        self.condition_false = condition_false
        self.condition_up = condition_up
        self.condition_down = condition_down

    def get_data_fields(self) -> set:
        result = [self.previous_field_a, self.current_field_a, self.field_b]
        result.extend( self.condition_up.get_data_fields())
        result.extend( self.condition_down.get_data_fields())
        result.extend( self.condition_false.get_data_fields())
        return set(result)

    @property
    def depth(self):
        return 1+max(self.condition_up.depth,
                     self.condition_down.depth,
                     self.condition_false.depth)

    @property
    def size(self):
        return 1 + self.condition_up.size + self.condition_down.size + self.condition_false.size

    def resolve(self, data) -> Node:
        """

        :param data:
        :return:
        """
        if data[self.previous_field_a] < data[self.field_b] < data[self.current_field_a]:
            return self.condition_up.resolve(data)
        elif data[self.previous_field_a] > data[self.field_b] > data[self.current_field_a]:
            return self.condition_down.resolve(data)
        else:
            return self.condition_false.resolve(data)

    def resolve_ga_fitness(self, data) -> Node:
        r = data[f'close#{self.field_b}']
        if r == 0:
            return self.condition_up.resolve_ga_fitness(data)
        elif r == 1:
            return self.condition_down.resolve_ga_fitness(data)
        else:
            return self.condition_false.resolve_ga_fitness(data)


    def find(self, target_index, current_index, replace:Node=None) -> (int, Node):
        """

        :param target_index:
        :param current_index:
        :return:
        """
        current_index += 1
        if current_index == target_index:
            if not replace is None:
                self.condition_up = replace
            return current_index, self.condition_up
        else:
            current_index, f = self.condition_up.find(target_index, current_index, replace)
            if not f is None:
                return current_index, f

        current_index += 1
        if current_index == target_index:
            if not replace is None:
                self.condition_down = replace
            return current_index, self.condition_down
        else:
            current_index, f = self.condition_down.find(target_index, current_index, replace)
            if not f is None:
                return current_index, f

        current_index += 1
        if current_index == target_index:
            if not replace is None:
                self.condition_false = replace
            return current_index, self.condition_false
        else:
            current_index, f = self.condition_false.find(target_index, current_index, replace)
            if not f is None:
                return current_index, f

        return current_index, None

    def __str__(self):
        return f"CROSS({self.current_field_a},{self.field_b}){{{self.condition_up},{self.condition_down},{self.condition_false}}}"

    def sanitise(self, parent_conditions:list=[])->Node:
        self.condition_up = self.condition_up.sanitise(parent_conditions + [[self.current_field_a, self.field_b, '>']])
        self.condition_down = self.condition_down.sanitise(parent_conditions + [[self.current_field_a, self.field_b, '<']])
        self.condition_false = self.condition_false.sanitise(parent_conditions)
        # Check self
        # If a and b in conditions
        matches = [c[2] for c in parent_conditions if c[0] == self.current_field_a and c[1] == self.field_b]
        # If sign >, return condition_true
        # if sign <, return condition_false
        # Otherwise return self
        if '>' in matches:
            return self.condition_up
        elif '<' in matches:
            return self.condition_down
        else:
            return self

    def compile(self)->str:
        return f"st.Cross('open', 'close_ask', '{self.field_b}', {self.condition_up.compile()}, {self.condition_down.compile()}, {self.condition_false.compile()})"


    def to_database_switch_case(self) -> list:
        result = []
        s = f"(({self.previous_field_a} < {self.field_b}) and ({self.field_b} < {self.current_field_a}))"
        if type(self.condition_up) == Leaf:
            result.append(f"{s} then '{self.condition_up.resolve(None)}'")
        else:
            r = self.condition_up.to_database_switch_case()
            for l in r:
                result.append(s + " and " + l)


        s = f"(({self.previous_field_a} > {self.field_b}) and ({self.field_b} > {self.current_field_a}))"
        if type(self.condition_down) == Leaf:
            result.append(f"{s} then '{self.condition_down.resolve(None)}'")
        else:
            r = self.condition_down.to_database_switch_case()
            for l in r:
                result.append(s + " and " + l)


        s = f"(({self.previous_field_a} > {self.field_b}) and ({self.current_field_a} > {self.field_b}))"
        if type(self.condition_false) == Leaf:
            result.append(f"{s} then '{self.condition_false.resolve(None)}'")
        else:
            r = self.condition_false.to_database_switch_case()
            for l in r:
                result.append(s + " and " + l)


        s = f"(({self.previous_field_a} < {self.field_b}) and ({self.current_field_a} < {self.field_b}))"
        if type(self.condition_false) == Leaf:
            result.append(f"{s} then '{self.condition_false.resolve(None)}'")
        else:
            r = self.condition_false.to_database_switch_case()
            for l in r:
                result.append(s + " and " + l)

        return result

    def to_function(self, indent:int=0) -> str:
        t = '\t'
        return f"{t*indent}if data['{self.previous_field_a}'] < data['{self.field_b}'] < data['{self.current_field_a}']:\n" \
               f"{self.condition_up.to_function(indent+1)}" \
               f"{t*indent}elif data['{self.previous_field_a}'] > data['{self.field_b}'] > data['{self.current_field_a}']:\n" \
               f"{self.condition_down.to_function(indent+1)}" \
               f"{t*indent}else:\n" \
               f"{self.condition_false.to_function(indent+1)}"
