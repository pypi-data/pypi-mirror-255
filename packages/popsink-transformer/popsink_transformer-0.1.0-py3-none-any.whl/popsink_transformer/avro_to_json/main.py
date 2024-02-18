"""AvroToJson manager."""


class AvroToJson:
    """AvroToJson class.

    Fixed and bytes fields are not yet fully compatible and are converted to string type.
    """

    AVRO_TO_JSON = {
        "int": "integer",
        "long": "integer",
        "float": "number",
        "double": "number",
        "record": "struct",
        "enum": "string",
        "bytes": "string",
        "map": "object",
        "fixed": "string",
    }

    def __init__(self, from_source: dict) -> None:
        self.from_source = from_source

    def convert(self) -> dict:
        """Convert an avro schema to a json schema."""
        json_schema = self.get_base_structure()

        if not self.from_source:
            return json_schema

        json_fields = []
        for field in self.from_source["fields"]:
            formatted_field = self.format_field(field)
            json_fields.append(formatted_field)

        json_schema["schema"]["fields"] = json_fields
        return json_schema

    def convert_avro_type_to_json_type(self, avro_type: str):
        """Convert avro type to json type."""
        return self.AVRO_TO_JSON.get(avro_type, avro_type)

    def format_field(self, field: dict) -> dict:
        """Call all the specific methods for field formatting."""
        json_field = {}
        json_field = self.write_optional_state(field, json_field)
        field = self.unwrap_complex_type(field)
        json_field = self.add_type(field, json_field)
        json_field = self.format_array(field, json_field)
        json_field = self.format_record(field, json_field)
        json_field = self.format_enum(field, json_field)
        json_field = self.format_map(field, json_field)
        json_field = self.format_uuid(field, json_field)
        json_field = self.format_date(field, json_field)
        json_field = self.convert_name_to_field(field, json_field)
        json_field["type"] = self.convert_avro_type_to_json_type(
            json_field["type"]
        )
        return json_field

    def add_type(self, field: dict, json_field: dict):
        """Add the type."""
        json_field["type"] = field["type"]
        return json_field

    def unwrap_complex_type(self, field: dict) -> dict:
        """Unwrap the complexe type if it is found."""
        if isinstance(field["type"], dict):
            wrapped_field: dict = field["type"]
            if "name" not in wrapped_field:
                wrapped_field["name"] = field["name"]
            return wrapped_field
        return field

    def get_base_structure(self) -> dict:
        """Return json schema base structure."""
        base_structure = {
            "schema": {
                "type": "struct",
                "optional": False,
                "fields": [],
            }
        }
        return base_structure

    def convert_name_to_field(self, field: dict, json_field: dict) -> dict:
        """Convert key 'name' to 'field'."""
        json_field["field"] = field["name"]
        return json_field

    def write_optional_state(self, field: dict, json_field: dict) -> dict:
        """Write the correct optional state - bool."""
        is_optional = False
        if isinstance(field["type"], list):
            real_type = [item for item in field["type"] if item != "null"][0]
            field["type"] = real_type
            is_optional = True
        json_field["optional"] = is_optional
        return json_field

    def format_array(self, field: dict, json_field: dict) -> dict:
        """Format array fields."""
        if field["type"] == "array":
            json_field["items"] = {
                "type": self.convert_avro_type_to_json_type(field["items"])
            }
        return json_field

    def format_record(self, field: dict, json_field: dict) -> dict:
        """Format record fields."""
        if field["type"] == "record":
            json_fields = []
            for inner_field in field["fields"]:
                formatted_field = self.format_field(inner_field)
                json_fields.append(formatted_field)
            json_field["fields"] = json_fields
        return json_field

    def format_enum(self, field: dict, json_field: dict) -> dict:
        """Format enum fields."""
        if field["type"] == "enum":
            json_field["enum"] = field["symbols"]
        return json_field

    def format_map(self, field: dict, json_field: dict) -> dict:
        """Format map fields."""
        if field["type"] == "map":
            json_field["patternProperties"] = {
                "*": {
                    "type": self.convert_avro_type_to_json_type(
                        field["values"]
                    )
                }
            }
        return json_field

    def format_uuid(self, field: dict, json_field: dict) -> dict:
        """Format uuid fields."""
        if field.get("logicalType") == "uuid":
            json_field["format"] = field["logicalType"]
        return json_field

    def format_date(self, field: dict, json_field: dict) -> dict:
        """Format date fields."""
        if field.get("logicalType") == "date":
            json_field["format"] = field["logicalType"]
            json_field["type"] = "string"
        return json_field
