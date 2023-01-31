from orcidlink import model
from orcidlink.service_clients import orcid_api


# "year": {"value": date_parts[0]},
# "month": {"value": date_parts[1].rjust(2, "0")},
# "day": {"value": date_parts[2].rjust(2, "0")},


def orcid_date_to_string_date(orcid_date: orcid_api.Date) -> str:
    # def pad(s: str) -> str:
    #     return s.lstrip('0').rjust(2, '0')

    def nopad(s: str) -> str:
        return s.lstrip("0")

    year = orcid_date.year.value
    if orcid_date.month is not None:
        month = orcid_date.month.value
    else:
        month = None

    if orcid_date.day is not None:
        day = orcid_date.day.value
    else:
        day = None

    if month is not None:
        if day is not None:
            return f"{year}/{nopad(month)}/{nopad(day)}"
        else:
            return f"{year}/{nopad(month)}"
    else:
        return f"{year}"


def transform_external_id(external_id: orcid_api.ORCIDExternalId) -> model.ExternalId:
    return model.ExternalId(
        type=external_id.external_id_type,
        value=external_id.external_id_value,
        url=external_id.external_id_url.value,
        relationship=external_id.external_id_relationship,
    )


def raw_work_summary_to_work(
    work_summary: orcid_api.WorkSummary,
) -> model.ORCIDWork:
    """
    Transforms an ORCID work record into a simpler work record as emitted by
    the api.
    """

    # TODO: should also get the source app id
    externalIds = []
    if work_summary.external_ids is not None:
        for external_id in work_summary.external_ids.external_id:
            externalIds.append(transform_external_id(external_id))

    return model.ORCIDWork(
        putCode=work_summary.put_code,
        createdAt=work_summary.created_date.value,
        updatedAt=work_summary.last_modified_date.value,
        source=work_summary.source.source_name.value,
        title=work_summary.title.title.value,
        journal=None
        if work_summary.journal_title is None
        else work_summary.journal_title.value,
        date=orcid_date_to_string_date(work_summary.publication_date),
        workType=work_summary.type,
        url=work_summary.url.value,
        externalIds=externalIds,
    )


def raw_work_to_work(work_summary: orcid_api.Work) -> model.ORCIDWork:
    """
    Transforms an ORCID work record into a simpler work record as emitted by
    the api.
    """
    put_code = work_summary.put_code
    created_at = work_summary.created_date.value
    updated_at = work_summary.last_modified_date.value

    # TODO: should also get the source app id
    source = work_summary.source.source_name.value
    date = orcid_date_to_string_date(work_summary.publication_date)
    title = work_summary.title.title.value
    journal = (
        None if work_summary.journal_title is None else work_summary.journal_title.value
    )
    work_type = work_summary.type
    url = work_summary.url.value

    # Now for external ids
    external_ids = []
    if work_summary.external_ids is not None:
        for external_id in work_summary.external_ids.external_id:
            external_ids.append(transform_external_id(external_id))

    return model.ORCIDWork.parse_obj(
        {
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
    )


# class ORCIDDateValue(TypedDict):
#     value: str
