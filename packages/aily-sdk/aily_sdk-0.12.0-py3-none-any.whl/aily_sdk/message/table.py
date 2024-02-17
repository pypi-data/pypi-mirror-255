from aily_sdk.message.record import MetaModel
from aily_sdk.message.utils import format_js_value


class Table(metaclass=MetaModel):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.to_message()

    def to_message(self):
        fields_str = ', '.join(
            field.to_table_meta() if hasattr(field, 'to_table_meta') else field.to_message()
            for field in self._fields.values()
        )
        formatted_items = []
        for item in self.data:
            formatted_item = ',\n'.join(f" {key}: {format_js_value(value)}" for key, value in item.items())
            formatted_items.append(f"{{{formatted_item}\n}}")

        data_str = f"{', '.join(formatted_items)}"

        return f"<table columns = [\n{fields_str}\n]\ndata = [\n    {data_str}\n] />"
