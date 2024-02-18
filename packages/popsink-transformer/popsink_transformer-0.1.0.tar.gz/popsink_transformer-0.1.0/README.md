# Transformer Library

This library provides a set of tools to transform Avro schemas into various formats such as JSON schema, SQL for Apache Flink, and PostgreSQL SQL. Additionally, it can transform data from these formats back into Avro schemas. Whether you're working with Avro schemas in your data pipeline or database schema, this library aims to simplify the conversion process for you.

## Features

- Convert Avro schema to JSON schema.
- Generate SQL statements for Apache Flink based on Avro schema.
- Generate PostgreSQL SQL statements based on Avro schema.

## Usage

Here's a quick guide on how to use the library:

### 1. Convert Avro Schema to JSON Schema

```python
transformer = Transformer(from_source=avro_schema)
json_schema = transformer.avro_to_json.convert()
print(json_schema)
```

### 2. Generate SQL for Apache Flink

```python
transformer = Transformer(
    from_source=avro_schema,
    sql_type=SqlType.FLINK,
)
flink_sql = transformer.avro_to_sql.convert()
print(flink_sql)
```

### 3. Generate PostgreSQL SQL

```python
transformer = Transformer(
    from_source=avro_schema,
    sql_type=SqlType.POSTGRES,
)
postgres_sql = transformer.avro_to_sql.convert()
print(postgres_sql)
```
