from orcidlink.model import WorkUpdate
from orcidlink.service_clients import orcid_api


def parse_date(date_string: str) -> orcid_api.Date:
    date_parts = date_string.split("/")
    if len(date_parts) == 1:
        return orcid_api.Date(year=orcid_api.StringValue(value=date_parts[0]))
    elif len(date_parts) == 2:
        return orcid_api.Date(
            year=orcid_api.StringValue(value=date_parts[0]),
            month=orcid_api.StringValue(value=date_parts[1].rjust(2, "0")),
        )
    elif len(date_parts) == 3:
        return orcid_api.Date(
            year=orcid_api.StringValue(value=date_parts[0]),
            month=orcid_api.StringValue(value=date_parts[1].rjust(2, "0")),
            day=orcid_api.StringValue(value=date_parts[2].rjust(2, "0")),
        )
    else:
        raise ValueError(
            f"Date must have 1-3 parts; has {len(date_parts)}: {date_string}"
        )


# TODO: return should be class
def translate_work_update(
    work_update: WorkUpdate, work_record: orcid_api.Work
) -> orcid_api.Work:
    #
    # TODO: detected error (status code) HERE
    #

    #
    # Then modify it from the request body
    #
    if work_update.title is not None:
        work_record.title.title.value = work_update.title

    if work_update.workType is not None:
        work_record.type = work_update.workType

    if work_update.journal is not None:
        work_record.journal_title = orcid_api.StringValue(value=work_update.journal)

    if work_update.date is not None:
        work_record.publication_date = orcid_api.Date.parse_obj(
            parse_date(work_update.date)
        )

    if work_update.workType is not None:
        work_record.type = work_update.workType

    if work_update.url is not None:
        work_record.url.value = work_update.url

    if work_update.externalIds is not None:
        for index, externalId in enumerate(work_update.externalIds):
            if index < len(work_record.external_ids.external_id):
                external_id = work_record.external_ids.external_id[index]
                external_id.external_id_type = externalId.type
                external_id.external_id_value = externalId.value
                external_id.external_id_url = orcid_api.StringValue(
                    value=externalId.url
                )
                external_id.external_id_relationship = externalId.relationship
            else:
                # for work update external ids beyond the last work record
                # external id. Allows "adding" new external ids
                id = orcid_api.ORCIDExternalId(
                    external_id_type=externalId.type,
                    external_id_value=externalId.value,
                    external_id_normalized=None,
                    external_id_url=orcid_api.StringValue(value=externalId.url),
                    external_id_relationship=externalId.relationship,
                )
                work_record.external_ids.external_id.append(
                    orcid_api.ORCIDExternalId(
                        external_id_type=externalId.type,
                        external_id_value=externalId.value,
                        external_id_normalized=None,
                        external_id_url=orcid_api.StringValue(value=externalId.url),
                        external_id_relationship=externalId.relationship,
                    )
                )

    return work_record
