from .property_type import PropertyType
from .result_property import ResultProperty
import base64

class Result:
    id = 0
    job_id = 0
    generation = 0
    best_tree = ""
    properties = None

    def __init__(self):
        self.properties = []

    def __repr__(self):
        return f'<Result {self.id}>'
    
    def add_property(self, property_type:PropertyType, value:float):
        r = ResultProperty()
        r.property_type = property_type
        r.property_type_id = property_type.value
        r.value = value
        self.properties.append(r)

    def to_dict(self):
        d = {
            "id": self.id,
            "job_id": self.job_id,
            "generation": self.generation,
            "best_tree": base64.b64encode(self.best_tree),
            "properties": [p.to_dict() for p in self.properties]
        }
        return d