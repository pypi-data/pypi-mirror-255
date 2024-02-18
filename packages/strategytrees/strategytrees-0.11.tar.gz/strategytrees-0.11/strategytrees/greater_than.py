from . import Node
from . import Binary
from . import Leaf

class GreaterThan(Binary):

    def resolve(self, data) -> Node:
        """

        :param data:
        :return:
        """
        fb_val = self.field_b
        if not type(self.field_b) is int:
            fb_val = data[self.field_b]

        if data[self.field_a] > fb_val:
            return self.condition_true.resolve(data)
        else:
            return self.condition_false.resolve(data)

    def resolve_ga_fitness(self, data) -> Node:
        if data[f'{self.field_a}>{self.field_b_og}'] == 1:
            return self.condition_true.resolve_ga_fitness(data)
        else:
            return self.condition_false.resolve_ga_fitness(data)

    def __str__(self):
        return f"GT({self.field_a},{self.field_b}){{{self.condition_true},{self.condition_false}}}"

    def sanitise(self, parent_conditions:list=[])->Node:
        f_b = f"{{int}}{self.field_b}"
        if not type(self.field_b) is int:
            f_b = self.field_b

        # Check condition_true
        self.condition_true = self.condition_true.sanitise(parent_conditions + [[self.field_a, f_b, '>']])
        # Check condition_false
        self.condition_false = self.condition_false.sanitise(parent_conditions + [[self.field_a, f_b, '<']])
        # If both children are leaves, test that
        if type(self.condition_true) is Leaf and type(self.condition_false) is Leaf:
            if self.condition_true.value == self.condition_false.value:
                return self.condition_true
        # Check self
        # If a and b in conditions
        matches = [c[2] for c in parent_conditions if c[0] == self.field_a and c[1] == f_b]
        # If sign >, return condition_true
        # if sign <, return condition_false
        # Otherwise return self
        if '>' in matches:
            return self.condition_true
        elif '<' in matches:
            return self.condition_false
        else:
            return self

    def compile(self)->str:
        f_b = f"{{int}}{self.field_b}"
        if not type(self.field_b) is int:
            f_b = self.field_b

        return f"st.GreaterThan('{self.field_a}', '{f_b}', {self.condition_true.compile()}, {self.condition_false.compile()})"

    def to_database_switch_case(self) -> list:
        result = []
        s = f"({self.field_a} > {self.field_b})"
        if type(self.condition_true) == Leaf:
            result.append(f"{s} then '{self.condition_true.resolve(None)}'")
        else:
            r = self.condition_true.to_database_switch_case()
            for l in r:
                result.append(s + " and " + l)

        s = f"({self.field_a} < {self.field_b})"
        if type(self.condition_false) == Leaf:
            result.append(f"{s} then '{self.condition_false.resolve(None)}'")
        else:
            r = self.condition_false.to_database_switch_case()
            for l in r:
                result.append(s + " and " + l)
        return result

    def to_function(self, indent:int=0) -> str:
        t = '\t'
        f_b = self.field_b
        if not type(self.field_b) is int:
            f_b = f"data['{self.field_b}']"

        return f"{t*indent}if data['{self.field_a}'] > {f_b}:\n" \
               f"{self.condition_true.to_function(indent+1)}" \
               f"{t*indent}else:\n" \
               f"{self.condition_false.to_function(indent+1)}"
