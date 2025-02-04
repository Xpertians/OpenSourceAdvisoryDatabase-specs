import json
import jsonschema
import argparse

def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None

def validate_json(schema_file, data_file):
    schema = load_json(schema_file)
    data = load_json(data_file)
    if schema is None or data is None:
        return

    try:
        jsonschema.validate(instance=data, schema=schema)
        print(f"Validation successful: {data_file} conforms to {schema_file}")
    except jsonschema.exceptions.ValidationError as e:
        print(f"Validation failed: {e.message}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate an OSSA JSON file against a schema.")
    parser.add_argument("schema_file", help="Path to the OSSA schema file (JSON Schema)")
    parser.add_argument("data_file", help="Path to the OSSA data file to validate")
    args = parser.parse_args()
    validate_json(args.schema_file, args.data_file)
