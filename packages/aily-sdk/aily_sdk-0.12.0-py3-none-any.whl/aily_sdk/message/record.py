# my_package/message/record.py

from .field import Field, StringField
from .utils import format_js_value


class MetaModel(type):
    def __new__(mcs, name, bases, namespace):
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key  # Set the name of the field based on the attribute name
                fields[key] = value
        namespace['_fields'] = fields
        return super().__new__(mcs, name, bases, namespace)


class Record(metaclass=MetaModel):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._fields:
                setattr(self, key, value)
            else:
                raise ValueError(f"Field {key} does not exist in {type(self).__name__}")

    def __str__(self):
        return self.to_message()

    def to_message(self):
        fields_str = ', '.join(field.to_message() for field in self._fields.values())
        data_str = ',\n    '.join(f"{name}: {format_js_value(getattr(self, name))}" for name in self._fields)
        return f"<record fields = [\n{fields_str}\n]\ndata = {{\n    {data_str}\n}}\n/>"
