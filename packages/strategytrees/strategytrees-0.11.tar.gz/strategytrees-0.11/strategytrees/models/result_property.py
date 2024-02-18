from .property_type import PropertyType


class ResultProperty:
    property_type:PropertyType = None
    value = 0
    
    def __repr__(self):
        return f'<ResultProperty {self.id}>'

    def to_dict(self):
        d = {
            "property_type_id" : self.property_type.value,
            "value" : self.value
        }
        return d
