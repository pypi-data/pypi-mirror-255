"""AvroToSQL manager."""


from enum import Enum


class SqlType(Enum):
    """SQL types supported."""

    POSTGRES = "postgres"
    FLINK = "flink"


class AvroToSQL:
    """AvroToSQL class.

    Note: This class is designed to convert Avro fields into SQL-readable types.
    It does not perform the conversion of entire Avro schemas to SQL queries.
    """

    def __init__(self, from_source: dict, sql_type: SqlType) -> None:
        self.from_source = from_source
        self.sql_type = sql_type

    def convert(self) -> dict:
        """Convert an avro schema to an SQL schema."""
        if not self.from_source:
            return ""

        sql_fields = []
        for avro_field in self.from_source["fields"]:
            formatted_field = self.format_field(avro_field)
            sql_fields.append(formatted_field)

        sql_schema = ",".join(sql_fields)
        return sql_schema

    def format_field(self, avro_field: dict) -> dict:
        """Call all the specific methods for field formatting."""
        sql_field = ""
        sql_field = self.unwrap_field(avro_field, sql_field)
        sql_field = self.write_nullable(avro_field, sql_field)
        sql_field = self.format_array(avro_field, sql_field)
        sql_field = self.convert_avro_type_to_sql_type(sql_field)
        sql_field = self.format_record(avro_field, sql_field)
        sql_field = self.format_map(avro_field, sql_field)
        return sql_field

    def unwrap_field(self, avro_field: dict, sql_field: str):
        """Unwrap avro field."""
        avro_field_type = avro_field["type"]

        if avro_field.get("logicalType"):
            avro_field_type = avro_field["logicalType"]

        if isinstance(avro_field_type, list):
            avro_field_type = [
                value for value in avro_field_type if value != "null"
            ].pop()

        if isinstance(avro_field_type, dict):
            avro_field_type = avro_field_type["type"]

        sql_field = f'`{avro_field["name"]}` {avro_field_type}'
        return sql_field

    def get_avro_to_sql_mapping(self):
        """Get the appropriate Avro to SQL mapping based on the SQL type."""
        if self.sql_type is SqlType.POSTGRES:
            return {
                "boolean": "BOOLEAN",
                "int": "INTEGER",
                "long": "BIGINT",
                "float": "REAL",
                "double": "DOUBLE PRECISION",
                "bytes": "BIT",
                "string": "STRING",
                "enum": "JSON",
                "fixed": "JSON",
                "uuid": "UUID",
                "date": "DATE",
            }

        if self.sql_type is SqlType.FLINK:
            return {
                "boolean": "BOOLEAN",
                "int": "INTEGER",
                "long": "BIGINT",
                "float": "FLOAT",
                "double": "DOUBLE",
                "bytes": "BYTES",
                "string": "STRING",
                "enum": "STRING",
                "fixed": "DECIMAL",
                "date": "DATE",
                "uuid": "STRING",
            }
        raise ValueError("Incorrect SQL type has been specified.")

    def write_nullable(self, avro_field: str, sql_field: str):
        """Write the nullable state at the end of the field."""
        if (
            not isinstance(avro_field["type"], list)
            and avro_field["type"] != "record"
        ):
            sql_field += " NOT NULL"
        return sql_field

    def format_array(self, avro_field: dict, sql_field: str):
        """Format array fields."""
        if "array" in sql_field:
            if self.sql_type is SqlType.POSTGRES:
                sql_field = sql_field.replace(
                    "array", f"{avro_field['type']['items']} ARRAY"
                )
            if self.sql_type is SqlType.FLINK:
                sql_field = sql_field.replace(
                    "array", f"ARRAY<{avro_field['type']['items']}>"
                )
        return sql_field

    def format_map(self, avro_field: dict, sql_field: str):
        """Format map fields."""
        if "map" in sql_field:
            if self.sql_type is SqlType.POSTGRES:
                sql_field = sql_field.replace("map", "JSON")

            if self.sql_type is SqlType.FLINK:
                map_type = avro_field["type"]["values"].upper()
                sql_field = sql_field.replace(
                    "map", f"MAP<{map_type}, {map_type}>"
                )
        return sql_field

    def format_record(self, avro_field: dict, sql_field: str):
        """Format record fields."""
        if "record" in sql_field:
            if self.sql_type is SqlType.POSTGRES:
                sql_field = sql_field.replace("record", "JSON")

            if self.sql_type is SqlType.FLINK:
                field_header = []
                for field in avro_field["fields"]:
                    formatted_field = self.format_field(field)
                    field_header.append(formatted_field)

                header = ", ".join(field_header)
                sql_field = sql_field.replace("record", f"ROW<{header}>")

                field_body = []
                record_name = avro_field["name"]
                for field in avro_field["fields"]:
                    field_name = field["name"]
                    line = f"`{field_name}` AS `{record_name}`.`{field_name}`"
                    field_body.append(line)

                body = ",".join(field_body)
                sql_field += f",{body}"
        return sql_field

    def convert_avro_type_to_sql_type(self, sql_field: str):
        """Convert avro type to SQL type.

        We replace the avro type with one space before to not mistake it with
        the name of the field.

        Example: '`date` date'
        """
        for avro_type, sql_type in self.get_avro_to_sql_mapping().items():
            if avro_type in sql_field:
                sql_field = sql_field.replace(f" {avro_type}", f" {sql_type}")
                if self.sql_type is SqlType.FLINK:
                    sql_field = sql_field.replace(
                        f"<{avro_type}>", f"<{sql_type}>"
                    )
        return sql_field
