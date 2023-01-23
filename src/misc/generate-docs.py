import json
from typing import Any, List

from orcidlink.lib.utils import get_prop


def flatten(md: List[Any]):
    flat = []

    def loop(a_list: List[Any]):
        for item in a_list:
            if isinstance(item, str):
                flat.append(item)
            elif isinstance(item, list):
                loop(item)

    loop(md)
    return flat


def render_markdown_list(md):
    return "\n".join(flatten(md))


def render_html_list(md):
    return "".join(flatten(md))


def save_markdown(markdown: List[str], file: str):
    with open(f"/kb/module/docs/api/{file}", "w") as fout:
        fout.write(render_markdown_list(markdown))


def md_line():
    return "\n"


def generate_table_row(row):
    return f"|{'|'.join(row)}|"


def generate_table(header, rows):
    md = []
    md.append(generate_table_row(header))
    md.append(generate_table_row(["----" for _ in header]))
    for row in rows:
        md.append(generate_table_row(row))
    return md


def generate_html_table_row(row, tag="td", widths=None):
    return ["<tr>", [[f"<{tag}>", item, f"</{tag}>"] for item in row], "</tr>"]


def generate_html_table(header, rows, widths=None):
    md = []
    md.append('<table style="width: 100%;">')
    md.append("<thead>")
    md.append(generate_html_table_row(header, "th"))
    md.append("</thead>")
    if widths is not None:
        md.append("<colgroup>")
        for width in widths:
            if width is not None:
                md.append(f'<col style="width: {width};">')
            else:
                md.append(f"<col>")
        md.append("</colgroup>")
    md.append("<tbody>")
    for row in rows:
        md.append(generate_html_table_row(row))
    md.append("</tbody>")
    md.append("</table>")
    return render_html_list(md)


#
# Implementation
#


def md_header(text: str, level: int = 1):
    header_tag = "#" * level
    return [f"{header_tag} {text}", md_line()]


def generate_header(spec: dict):
    md = []

    # Title and header
    md.append(md_header(spec["info"]["title"], 1))
    md.append(spec["info"]["version"])
    md.append(spec["info"]["description"])

    return md


def generate_paths(spec: dict):
    md = []
    md.append(md_header("Paths", 2))
    for path, path_spec in spec["paths"].items():
        md.append(md_header(path, 3))
        md.append(generate_path(path_spec))

    return md


def md_tags(tags):
    return f'tags: {", ".join(tags)}'


def generate_response_contentx(content):
    if content is None:
        return "n/a"

    md = []
    for content_type, spec in content.items():
        md.append(f"**{content_type}**")
    return md


def generate_property_type(spec):
    if "$ref" in spec:
        link = spec["$ref"]
        name = link.split("/")[3]
        return f'<a href="#{name}">{name}</a>'
    elif "type" in spec:
        return spec["type"]
    else:
        return "n/a"


def generate_schema(schema):
    if "$ref" in schema:
        link = schema["$ref"]
        name = link.split("/")[3]
        return f'<a href="#{name}">{name}</a>'
    elif "type" in schema:
        return schema["type"]
    elif "anyOf" in schema:
        # this goes inside a table so annoyingly we need to
        # generate this as html..
        html = ""

        html += "<div><i>Any Of</i></div>"
        for any_of in schema["anyOf"]:
            html += f"<div>{generate_data_type_content(any_of)}</div>"
        return html
    else:
        print("NOT HANDLED", schema)
        return "!! NOT HANDLED !!"


def generate_data_type_content(schema):
    if "$ref" in schema:
        link = schema["$ref"]
        name = link.split("/")[3]
        return f'<a href="#{name}">{name}</a>'
    elif "anyOf" in schema:
        md = []
        md.append("Any Of  ")
        for any_of in schema["anyOf"]:
            md.append(f"- {generate_data_type_content(any_of)}")
    else:
        print("NOT HANDLED", schema)
        return "!! NOT HANDLED !!"


def generate_response_content(content):
    if content is None:
        return "<i>none</i>"

    # The response, if any, should always be
    # application/json, so we just assume that.
    json_content_type = prop(content, "application/json")
    if json_content_type is None:
        return list(content)[0]
        # return 'NOT JSON!'

    schema = prop(json_content_type, "schema")
    if schema is None:
        return "NO TYPE!"

    result = generate_schema(schema)
    if result == "!! NOT HANDLED !!":
        print("hmm", json_content_type)
    return result

    # rows = []
    # for content_type, spec in content.items():
    #     rows.append([
    #         content_type,
    #         generate_data_type_content(spec)
    #     ])
    # return generate_html_table(
    #     ['Content Type', 'Data Type'],
    #     rows
    # )


def generate_responsesx(responses):
    md = []
    for status_code, spec in responses.items():
        md.append(md_header(status_code, 5))
        md.append(spec.get("description", "n/a"))
        md.append(md_header("Content Types", 5))

        md.append(generate_response_content(spec.get("content")))
    return md


def generate_responses(responses):
    rows = []
    for status_code, spec in responses.items():
        rows.append(
            [
                status_code,
                spec.get("description", "n/a"),
                generate_response_content(spec.get("content")),
            ]
        )
    return generate_html_table(
        ["Status Code", "Description", "Type"], rows, widths=["8em", None, "10em"]
    )


def prop(value, path, default_value=None):
    if isinstance(path, str):
        path = path.split(".")
    value, found = get_prop(value, path)
    if not found:
        return default_value
    return value


def generate_parameters(parameters):
    if parameters is None:
        return "*none*"
    # One table for now...
    rows = []
    for parameter in parameters:
        rows.append(
            [
                prop(parameter, "name", "n/a"),
                prop(parameter, "description", "n/a"),
                prop(parameter, ["schema", "type"], "n/a"),
                prop(parameter, "in", "n/a"),
            ]
        )
    return generate_html_table(["Name", "Description", "Type", "In"], rows)


def generate_path(spec: dict):
    md = []
    for method, method_spec in spec.items():
        md.append(md_header(method, 4))
        # md.append(md_tags(method_spec.get('tags', 'n/a')))
        # md.append(md_line())
        md.append(method_spec.get("summary", "n/a"))
        md.append(md_line())
        md.append(method_spec.get("description", "n/a"))
        md.append(md_line())
        md.append(md_header("Input", 4))
        md.append(generate_parameters(method_spec.get("parameters")))
        md.append(md_line())
        md.append(md_header("Output", 4))
        md.append(generate_responses(method_spec.get("responses")))
        md.append(md_line())
    return md


def generate_path2(spec: dict):
    path = prop(spec, "path")
    method = prop(spec, "method")
    method_spec = prop(spec, "spec")
    md = []
    md.append(md_header(f"{method.upper()} {path}", 4))
    # md.append(md_tags(method_spec.get('tags', 'n/a')))
    # md.append(md_line())
    # md.append(method_spec.get('summary', 'n/a'))
    # md.append(md_line())
    md.append(method_spec.get("description", "n/a"))
    md.append(md_line())
    md.append(md_header("Input", 4))
    md.append(generate_parameters(method_spec.get("parameters")))
    md.append(md_line())
    md.append(md_header("Output", 4))
    md.append(generate_responses(method_spec.get("responses")))
    md.append(md_line())
    return md


def generate_properties(required, properties):
    rows = []

    for field_name, field_spec in properties.items():
        rows.append(
            [
                field_name,
                generate_property_type(field_spec),
                "✓" if field_name in required else "",
            ]
        )

    return generate_html_table(
        ["Name", "Type", "Required"], rows, widths=[None, "15em", "5em"]
    )


def generate_type(type_name, type_spec):
    # all types are objects, afaik.
    required = prop(type_spec, "required", [])
    properties = prop(type_spec, "properties", {})
    prop_table = generate_properties(required, properties)

    md = []
    md.append(md_header(type_name, 5))
    md.append(prop_table)
    md.append(md_line())
    return md


def generate_types(spec):
    schemas = prop(spec, "components.schemas")
    if schemas is None:
        return "Strange, no types!"

    return [
        generate_type(type_name, type_spec) for type_name, type_spec in schemas.items()
    ]


# def main_plain():
#     with open("/kb/module/docs/api/openapi.json", "r") as fin:
#         spec = json.load(fin)
#         md = []
#         md.append(generate_header(spec))
#         md.append(generate_paths(spec))
#         md.append(generate_types(spec))
#         md.append("-fin-")
#     save_markdown(md, "index.md")


def generate_tag_paths(tags_map):
    md = []
    for tag, tag_spec in tags_map.items():
        md.append(md_header(tag, 2))
        md.append(tag_spec["description"])
        for path in tag_spec["paths"]:
            md.append(generate_path2(path))
        md.append(md_line())

    return md


def main():
    with open("/kb/module/docs/api/openapi.json", "r") as fin:
        spec = json.load(fin)
        md = []
        md.append(generate_header(spec))

        # Organize by tags. Assumes only one tag per link.
        tags_map = {}
        for tag in spec["tags"]:
            tag["paths"] = []
            tags_map[tag["name"]] = tag

        for path, path_spec in prop(spec, "paths").items():
            for method, method_spec in path_spec.items():
                tag = prop(method_spec, ["tags", 0])
                tags_map[tag]["paths"].append(
                    {"path": path, "method": method, "spec": method_spec}
                )

        md.append(generate_tag_paths(tags_map))

        md.append(generate_types(spec))
        md.append("-fin-")
    save_markdown(md, "index.md")


main()
