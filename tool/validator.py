import json
import jsonschema
from jsonschema import validate
import argparse

def validate_advisory(advisory_file, schema_file):
    try:
        # Load advisory and schema from external files
        with open(schema_file, 'r') as schema_f:
            schema = json.load(schema_f)
        
        with open(advisory_file, 'r') as advisory_f:
            advisory_json = json.load(advisory_f)

        # Validate the advisory
        validate(instance=advisory_json, schema=schema)
        print("Advisory is valid.")
    except jsonschema.exceptions.ValidationError as err:
        print(f"Validation error: {err.message}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Validate an OSS advisory JSON file against a schema.")
    parser.add_argument("advisory_file", type=str, help="Path to the advisory JSON file to validate.")
    parser.add_argument("schema_file", type=str, help="Path to the schema JSON file.")
    
    args = parser.parse_args()

    validate_advisory(args.advisory_file, args.schema_file)

if __name__ == "__main__":
    main()
