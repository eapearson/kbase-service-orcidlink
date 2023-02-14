import json
import sys
from typing import Any, List

from orcidlink.lib.json_file import get_prop
from orcidlink.lib.utils import http_client


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


def slugify(text: str) -> str:
    return text.replace(" ", "-").lower()


def render_markdown_list(md):
    return "\n".join(flatten(md))


def render_html_list(md):
    return "".join(flatten(md))


def save_markdown(markdown: List[str], file: str, dest: str):
    with open(f"/{dest}/docs/api/{file}", "w") as fout:
        fout.write(render_markdown_list(markdown))


def save_markdown_rendered(markdown: List[str], file: str, dest: str):
    content = json.dumps({"text": render_markdown_list(markdown), "mode": "gfm"})
    result = http_client().post(
        "https://api.github.com/markdown",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        },
        content=content,
    )
    doc = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link type="text/css" rel="stylesheet" href="gfm.css">
</head>
<body class="markdown-body">
{result.text}
</body>
</html>
"""
    with open(f"{dest}/docs/api/{file}", "w") as fout:
        fout.write(doc)


def md_line(n=1):
    return "\n" * n


def generate_table_row(row):
    return f"|{'|'.join(row)}|"


def generate_table(header, rows):
    md = []
    md.append(generate_table_row(header))
    md.append(generate_table_row(["----" for _ in header]))
    for row in rows:
        md.append(generate_table_row(row))
    return md


def generate_html_table_row(row, tag="td"):
    return ["<tr>", [[f"<{tag}>", item, f"</{tag}>"] for item in row], "</tr>"]


# def generate_html_table_header_row(row, tag="td", widths=None):
#     if widths is None:
#         return ["<tr>", [[f"<{tag}>", item, f"</{tag}>"] for item in row], "</tr>"]
#
#     md = []
#     md.append('<tr>')
#     for index, item in enumerate(row):
#         width = widths[index]
#         if width is None:
#             md.append(['<th>', item, '</th>'])
#         else:
#             md.append(['<th>', item, '</th>'])


def generate_html_table_width_rows(header, widths, tag="td"):
    if widths is None:
        return []
    md = []
    # full width row
    md.append(
        [
            "<tr>",
            f'<{tag} colspan="{len(header)}">',
            '<img width="2000px">',
            f"</{tag}>",
            "</tr>",
        ]
    )
    md.append("<tr>")
    for width in widths:
        if width is None:
            md.append(["<th>", "</th>"])
        else:
            md.append(["<th>", f'<img width="{width}">', "</th>"])
    return md


def generate_html_table(header, rows, widths=None):
    md = []
    md.append("<table>")
    md.append("<thead>")
    md.append(generate_html_table_width_rows(header, widths, "th"))
    md.append(generate_html_table_row(header, "th"))
    md.append("</thead>")
    # if widths is not None:
    #     md.append("<colgroup>")
    #     for width in widths:
    #         if width is not None:
    #             md.append(f'<col style="width: {width};">')
    #         else:
    #             md.append(f"<col>")
    #     md.append("</colgroup>")
    md.append("<tbody>")
    for row in rows:
        md.append(generate_html_table_row(row))
    md.append("</tbody>")
    md.append("</table>")
    return render_html_list(md)


#
# Implementation
#


def md_header(text: str, level: int = 1, anchor_prefix=None):
    header_tag = "#" * level
    anchor_prefix = "" if anchor_prefix is None else f"{anchor_prefix}_"
    header_anchor = f'<a name="header_{anchor_prefix}{slugify(text)}"></a>'
    return [header_anchor, f"{header_tag} {text}"]


def generate_usage():
    return f"""\
## Usage

This document is primarily generated from the `openapi` interface generated 
by <a href="https://fastapi.tiangolo.com">FastAPI</a>.

The {generate_anchor_link('Endpoints', 'header')} section documents all REST endpoints, including the 
expected responses, input parameters and output JSON and type definitions.

The {generate_anchor_link('Types', 'header')} section defines all of the Pydantic models used in the codebase, 
most of which are in service of the input and output types mentioned above.

### Issues

- Due to limitations of GitHub's markdown support, tables have two empty rows at the start of the header. This is \
due to the fact that GitHub does not allow any table formatting instructions, so we need to use the first two rows to \
establish the table and column widths. 
"""


def generate_toc():
    return f"""\
## Table of Contents    

- {generate_anchor_link('Endpoints')}
    - {generate_anchor_link('misc')}
    - {generate_anchor_link('link')}
    - {generate_anchor_link('linking-sessions')}
    - {generate_anchor_link('orcid')}
    - {generate_anchor_link('works')}
- {generate_anchor_link('Types')}
- {generate_anchor_link('Glossary')}

"""


def generate_html_link(url: str) -> str:
    # NB: Alas, cannot use target in GFM
    x = f'<a href="{url}">{url}</a>'
    return x


def md_line_break():
    return "  "


def generate_header(spec: dict):
    return [
        md_header(spec["info"]["title"], 1),
        f'<table><tr><td>version: {spec["info"]["version"]}</td></tr></table>',
        md_line(),
        spec["info"]["description"],
        md_header("Terms of Service", 2),
        generate_html_link(spec["info"]["termsOfService"]),
        md_header("Contact", 2),
        spec["info"]["contact"]["name"] + md_line_break(),
        generate_html_link(spec["info"]["contact"]["url"]) + md_line_break(),
        spec["info"]["contact"]["email"],
        md_header("License", 2),
        spec["info"]["license"]["name"],
        generate_html_link(spec["info"]["license"]["url"]),
        generate_usage(),
    ]


def md_tags(tags):
    return f'tags: {", ".join(tags)}'


def generate_schema(schema):
    if "$ref" in schema:
        link = schema["$ref"]
        name = link.split("/")[3]
        return generate_anchor_link(name, "header_type", render="html")
        # return f'<a href="#header_type_{slugify(name)}">{name}</a>'
    elif "type" in schema:
        return schema["type"]
    elif "anyOf" in schema:
        # this goes inside a table so annoyingly we need to
        # generate this as html..
        html = "<div><i>Any Of</i></div>"
        for any_of in schema["anyOf"]:
            html += f"<div>{generate_schema(any_of)}</div>"
        return html
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

    schema = prop(json_content_type, "schema")
    if schema is None:
        return "NO TYPE!"

    return generate_schema(schema)


def generate_responses(responses):
    rows = []
    for status_code, spec in dict(sorted(responses.items())).items():
        rows.append(
            [
                status_code,
                spec.get("description", "n/a"),
                generate_response_content(spec.get("content")),
            ]
        )
    return generate_html_table(
        ["Status Code", "Description", "Type"],
        rows,
        widths=["150px", "1000px", "150px"],
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
    widths = ["150px", "1000px", "150px", "150px"]
    return generate_html_table(
        ["Name", "Description", "Type", "In"], rows, widths=widths
    )


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
    md.append("---")
    return md


def generate_properties(required, properties):
    rows = []

    for field_name, field_spec in properties.items():
        rows.append(
            [
                field_name,
                generate_schema(field_spec),
                "✓" if field_name in required else "",
            ]
        )

    return generate_html_table(
        ["Name", "Type", "Required"], rows, widths=["1000px", "200px", "75px"]
    )


def generate_type(type_name, type_spec):
    # all types are objects, afaik.
    required = prop(type_spec, "required", [])
    properties = prop(type_spec, "properties", {})
    prop_table = generate_properties(required, properties)

    return [
        md_header(type_name, 5, anchor_prefix="type"),
        prop(type_spec, "description", ""),
        prop_table,
        md_line(2),
    ]


def generate_types(spec):
    schemas = prop(spec, "components.schemas")
    if schemas is None:
        return "Strange, no types!"

    return [
        generate_type(type_name, type_spec) for type_name, type_spec in schemas.items()
    ]


def generate_tag_paths(tags_map):
    md = []
    for tag, tag_spec in tags_map.items():
        md.append(md_header(tag, 3))
        md.append(tag_spec["description"])
        for path in tag_spec["paths"]:
            md.append(generate_path2(path))
        md.append(md_line())

    return md


def generate_anchor(prefix, term):
    slug = slugify(term)
    return f'<a name="{prefix}_{slug}"></a>'


def generate_anchor_link(label, prefix="header", term=None, render="markdown"):
    term = label if term is None else term
    slug = slugify(term)
    href = f"#user-content-{prefix}_{slug}"
    if render == "markdown":
        return f"[{label}]({href})"
    elif render == "html":
        return f'<a href="{href}">{label}</a>'
    else:
        raise ValueError(f"Unknown render method '{render}'")


def generate_glossary():
    terms = [
        {
            "term": "ORCID",
            "definition": "Open Researcher and Contributor ID",
            "link": "https://orcid.org",
        },
        {
            "term": "Public link record",
            "definition": "The record used internally to associate a KBase User Account with an ORCID Account,"
            + " with sensitive information such as tokens removed. Represented by "
            + "the type "
            + generate_anchor_link("LinkRecordPublic", "header_type", render="html"),
        },
    ]

    md = ["<dl>"]
    for term in terms:
        anchor = generate_anchor("glossary_term", term["term"])
        if "link" in term:
            md.append(
                [
                    f"<dt>{anchor}<a href='{term['link']}'>{term['term']}</a></dt><dd>{term['definition']}"
                ]
            )
        else:
            md.append(f"<dt>{anchor}{term['term']}</dt><dd>{term['definition']}</dd>")
    md.append("</dl>")
    return md


def main():
    dest = sys.argv[1]
    with open(f"{dest}/docs/api/openapi.json", "r") as fin:
        spec = json.load(fin)

        md = []

        md.append(generate_header(spec))

        md.append(generate_toc())

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

        md.append(md_header("Endpoints", 2))
        md.append(generate_tag_paths(tags_map))

        md.append(md_header("Types", 2))
        md.append(
            """\
This section presents all types defined via FastAPI (Pydantic). They are ordered
alphabetically, which is fine for looking them up, but not for their relationships.

> TODO: a better presentation of related types
"""
        )
        md.append(generate_types(spec))

        md.append(md_header("Glossary", 2))
        md.append(generate_glossary())
        md.append("-fin-")
    save_markdown(md, "index.md", dest)
    save_markdown_rendered(md, "index.html", dest)


main()
