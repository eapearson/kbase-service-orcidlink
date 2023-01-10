from orcidlink.lib.utils import get_int_prop, get_raw_prop, get_string_prop, make_date


def raw_work_to_work(work_summary):
    """
    Transforms an ORCID work record into a simpler work record as emitted by
    the api.
    """
    put_code = get_int_prop(work_summary, ["put-code"], None)

    created_at = get_int_prop(work_summary, ["created-date", "value"], None)

    updated_at = get_int_prop(work_summary, ["last-modified-date", "value"], None)

    # TODO: should also get the source app id
    source = get_raw_prop(work_summary, ["source", "source-name", "value"], None)

    date = make_date(
        get_int_prop(work_summary, ["publication-date", "year", "value"]),
        get_int_prop(work_summary, ["publication-date", "month", "value"]),
        get_int_prop(work_summary, ["publication-date", "day", "value"]),
    )

    title = get_string_prop(work_summary, ["title", "title", "value"], None)

    journal = get_string_prop(work_summary, ["journal-title", "value"], None)

    work_type = get_string_prop(work_summary, ["type"], None)

    url = get_string_prop(work_summary, ["url", "value"], None)

    # Now for external ids
    external_ids = []
    for external_id in get_raw_prop(work_summary, ["external-ids", "external-id"], []):
        id_type = get_string_prop(external_id, ["external-id-type"])
        id_value = get_string_prop(external_id, ["external-id-value"])
        id_url = get_string_prop(external_id, ["external-id-url", "value"])
        id_relationship = get_string_prop(external_id, ["external-id-relationship"])
        external_ids.append(
            {
                "type": id_type,
                "value": id_value,
                "url": id_url,
                "relationship": id_relationship,
            }
        )

    return {
        "putCode": put_code,
        "createdAt": created_at,
        "updatedAt": updated_at,
        "source": source,
        "title": title,
        "journal": journal,
        "date": date,
        "workType": work_type,
        "url": url,
        "externalIds": external_ids,
    }


def parse_date(date_string):
    date_parts = date_string.split("/")
    if len(date_parts) == 1:
        return {
            "year": {
                "value": date_parts[0]
            }
        }
    elif len(date_parts) == 2:
        return {
            "year": {
                "value": date_parts[0]
            },
            "month": {
                "value": date_parts[1].rjust(2, "0")
            }
        }
    elif len(date_parts) == 3:
        return {
            "year": {
                "value": date_parts[0]
            },
            "month": {
                "value": date_parts[1].rjust(2, "0")
            },
            "day": {
                "value": date_parts[2].rjust(2, "0")
            },
        }
