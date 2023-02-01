import json
import sys

from fastapi.openapi.utils import get_openapi
from orcidlink.main import app


#
# In which we generate an openapi.json spec, and then compare it to the
# last one saved. If there is a difference, we print the diff and return
# an error code (1); otherwise we print nothing and return a success
# code (0).
#


def list_diff(list1: list, list2: list, context=[]):
    if len(list1) != len(list2):
        raise ValueError(f"list1 and list2 are different lengths: {context}")
    for index, el1 in enumerate(list1):
        el2 = list1[index]
        if isinstance(el1, dict):
            if isinstance(el2, dict):
                dict_diff(el1, el2, [*context, {"index": index}])
            else:
                raise ValueError(
                    f"element for index {index} is dict in 1, but {type(el2)} in 2"
                )
        elif isinstance(el1, list):
            if isinstance(el2, list):
                list_diff(el1, el2, [*context, {"index": index}])
            else:
                raise ValueError(
                    f"element for index {index} is list in 1, but {type(el2)} in 2"
                )
        elif el1 != el2:
            raise ValueError(
                f"element at position {index} is different between the two lists: {context}"
            )


def dict_diff(dict1: dict, dict2: dict, context=[]):
    keys1 = list(dict1.keys())
    keys2 = list(dict2.keys())
    list_diff(keys1, keys2, [*context, {"dict": "keys"}])
    for key in keys1:
        if key not in dict2:
            raise ValueError(f"key '{key}' not found in dict 2")
        el1 = dict1[key]
        el2 = dict2[key]
        if isinstance(el1, dict):
            if isinstance(el2, dict):
                dict_diff(el1, el2, [*context, {"dict": key}])
            else:
                raise ValueError(
                    f"element for key {key} is dict in 1, but {type(el2)} in 2"
                )
        elif isinstance(el1, list):
            if isinstance(el2, list):
                list_diff(el1, el2, [*context, {"dict": key}])
            else:
                raise ValueError(
                    f"element for key {key} is list in 1, but {type(el2)} in 2"
                )
        elif el1 != el2:
            raise ValueError(
                f"element for key {key} is different between the two lists: {context}"
            )


def main():
    with open("/kb/module/docs/api/openapi.json", "r") as fin:
        current_openapi = json.load(fin)

    new_openapi = json.loads(
        json.dumps(
            get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
                tags=app.openapi_tags,
                terms_of_service=app.terms_of_service,
                contact=app.contact,
                license_info=app.license_info,
            )
        )
    )

    try:
        dict_diff(current_openapi, new_openapi)
        print("openapi.json has no changes")
        sys.exit(0)
    except ValueError as ve:
        print("openapi.json would be different")
        print("please regenerate openapi.json and the associated docs")
        print(str(ve))
        sys.exit(1)


main()
