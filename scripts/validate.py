import json
from pathlib import Path
from jsonschema import validate, ValidationError

SCHEMA_PATH = Path("schema/wiu.schema.json")

def main():
    schema = json.load(open(SCHEMA_PATH))

    for file in Path("wius").glob("*.json"):
        print(f"Validating {file.name}...")
        data = json.load(open(file))

        try:
            validate(data, schema)
            print("OK")
        except ValidationError as e:
            print("ERROR:", e.message)

if __name__ == "__main__":
    main()
