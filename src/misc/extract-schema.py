import json
import sys


def extract(initial_type_name):
    # get openapi.json file
    with open("/app/docs/api/openapi.json", "r") as fin:
        openapi = json.load(fin)

    schemas = dict()

    def evaluate_schema(schema):
        if "$ref" in schema:
            # Handles type replaced with $ref
            add_schema(ref_type_name(schema["$ref"]))
        elif "type" in schema:
            if schema["type"] == "object":
                # Any of the object fields could be a ref, so we punt to
                # possibly_add_schema to inspect the schema.
                for key, value in schema["properties"].items():
                    evaluate_schema(value)
            if schema["type"] == "array":
                # Arrays are different - the items property describes
                # the type of each array element (homogenous)
                evaluate_schema(schema["items"])

        elif "allOf" in schema:
            # We treat allOf like arrays
            for value in schema["allOf"]:
                evaluate_schema(value)

        elif "oneOf" in schema:
            # We treat anyOf like arrays.
            for value in schema["oneOf"]:
                evaluate_schema(value)

    def add_schema(name):
        schemas[name] = openapi["components"]["schemas"][name]
        evaluate_schema(schemas[name])

    def ref_type_name(ref):
        ref_path = ref.split("/")[1:]
        return ref_path[-1:][0]

    # loop through fields fetching each $ref
    add_schema(initial_type_name)

    print(json.dumps(schemas))


def main(args):
    initial_type_name = args[0]
    print(f"Extracting types starting at {initial_type_name}")
    extract(initial_type_name)


if __name__ == "__main__":
    main(sys.argv[2:])
