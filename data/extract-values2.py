import json


def main():
    values = []
    with open("contributor-roles.json", "r") as work_types_file:
        types = json.load(work_types_file)
        for item in types:
            values.append(item['value'])

    print("VALUES")
    for value in values:
        print(value)

    print("")
    print("ENUM")
    for value in values:
        name = value.replace("-", "_")
        print(f'{name} = "{value}"')


main()
