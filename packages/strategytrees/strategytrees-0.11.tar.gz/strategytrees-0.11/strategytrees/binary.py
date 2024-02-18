from .node import Node


class Binary(Node):
    min_depth = 2
    selection_probability = 0.2
    n_inputs = 2
    edges = 2

    def __init__(self, field_a: object,
                 field_b: object,
                 condition_true: Node,
                 condition_false: Node):
        self.field_a = field_a
        self.field_b_og = field_b # Needed if field b is converted into an integer
        self.field_b = field_b

        try:
            if field_b.find('{int}') >= 0:
                self.field_b = int(field_b[5:])
        except ValueError as e:
            print("Error with ", field_b)
            raise e

        self.condition_true = condition_true
        self.condition_false = condition_false

    def get_data_fields(self) -> list:
        result = [self.field_a, self.field_b_og]
        result.extend( self.condition_true.get_data_fields())
        result.extend( self.condition_false.get_data_fields())
        return set(result)

    @property
    def depth(self):
        return 1+max(self.condition_true.depth, self.condition_false.depth)

    @property
    def size(self):
        return 1 + self.condition_true.size + self.condition_false.size

    def find(self, target_index, current_index, replace:Node=None) -> (int, Node):
        """

        :param target_index:
        :param current_index:
        :param replace:
        :return:
        """
        if current_index == target_index:
            if not replace is None:
                self = replace
            return current_index, self

        current_index += 1
        if current_index == target_index:
            if not replace is None:
                self.condition_true = replace
            return current_index, self.condition_true
        else:
            current_index, f = self.condition_true.find(target_index, current_index, replace)
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

