import json


def main():
    values = []
    with open("work-types.json", "r") as work_types_file:
        work_types = json.load(work_types_file)
        for group in work_types:
            for item in group['values']:
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
