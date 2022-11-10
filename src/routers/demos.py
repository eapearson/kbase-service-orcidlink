import uuid
from typing import List, Optional, Union

from fastapi import APIRouter, Header
from lib.auth import get_username
from lib.db import FileStorage
from lib.json_file import get_json_file
from lib.responses import error_response, exception_response
from lib.utils import current_time_millis
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/demos",
    # tags=["items"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


#
# Assistance for DOI application persistence.
# Perhaps this can be better thought of as narrative publication metadata,
# which eventually could be stored in the narrative itself.
#

# Step 1: Select narrative

class MinimalNarrativeInfo(BaseModel):
    title: str = Field(...)
    workspaceId: int = Field(...)
    objectId: int = Field(...)
    version: int = Field(...)
    ref: str = Field(...)
    owner: str = Field(...)


class NarrativeSectionResult(BaseModel):
    narrativeInfo: MinimalNarrativeInfo


class NarrativeSection(BaseModel):
    status: str
    params: None = Field(None)
    value: NarrativeSectionResult = Field(None)


# class Affiliation(BaseModel):
#     name: str
#     role: str
#     startYear: str
#     endYear: str = Field(None)

# class ExternalId(BaseModel):
#     type: str
#     value:  str
#     url:  str = Field(None)
#     relationship:  str

# class Publication(BaseModel):
#     putCode: str
#     createdAt: int
#     updatedAt: int
#     source: str
#     title: str
#     journal: str
#     date: str
#     publicationType: str
#     url: str = Field(None)
#     citationType: str
#     citation: str
#     citationDescription: str
#     externalIds: List(ExternalId)

# class ORCIDProfile(BaseModel):
#     orcidId: str
#     firstName: str
#     lastName: str
#     bio: str
#     affiliations: List(Affiliation) = Field([])
#     publications: List(Publication) = Field([])

# Step 2 - Citations

class Citation(BaseModel):
    doi: Union[str, None] = Field(...)
    citation: Union[str, None] = Field(...)
    source: str = Field(...)


class CitationSectionParams(BaseModel):
    narrativeInfo: MinimalNarrativeInfo


class CitationsSectionResult(BaseModel):
    citations: List[Citation]


class CitationsSection(BaseModel):
    status: str
    params: CitationSectionParams = Field(None)
    value: CitationsSectionResult = Field(None)


# Step 3 ORCID Link

class ORCIDLinkSectionResult(BaseModel):
    orcidId: str | None


class ORCIDLinkSection(BaseModel):
    status: str
    params: None = Field(None)
    value: ORCIDLinkSectionResult = Field(None)


# Step 4 - Author import from Narrative

class ImportableAuthor(BaseModel):
    username: str = Field(None)
    firstName: str = Field(None)
    middleName: str = Field(None)
    lastName: str = Field(None)
    orcidId: str = Field(None)
    institution: str = Field(None)


class AuthorsImportSectionParams(BaseModel):
    narrativeInfo: MinimalNarrativeInfo


class AuthorsImportSectionResult(BaseModel):
    authors: List[ImportableAuthor] = Field(...)


class AuthorsImportSection(BaseModel):
    status: str
    params: AuthorsImportSectionParams = Field(None)
    value: AuthorsImportSectionResult = Field(None)


# Step 4 - Author

class Author(BaseModel):
    firstName: str
    middleName: str = Field(None)
    lastName: str
    emailAddress: str
    orcidId: str = Field(None)
    institution: str


class AuthorsSectionParams(BaseModel):
    authors: List[ImportableAuthor]


class AuthorsSectionResult(BaseModel):
    authors: List[Author] = Field(None)


class AuthorsSection(BaseModel):
    status: str
    params: AuthorsSectionParams = Field(None)
    value: AuthorsSectionResult = Field(None)


# Step 5: Contract numbers

class ContractNumbers(BaseModel):
    doe: List[str] = Field([])
    other: List[str] = Field([])


class ContractsSectionResult(BaseModel):
    contractNumbers: ContractNumbers


class ContractsSection(BaseModel):
    status: str
    params: None = Field(None)
    value: ContractsSectionResult = Field(None)


# Step 6 - geolocation

class GeolocationData(BaseModel):
    latitude: int = Field(None)
    longitude: int = Field(None)


class GeolocationSectionResult(BaseModel):
    geolocationData: GeolocationData


class GeolocationSection(BaseModel):
    status: str
    params: None = Field(None)
    value: GeolocationSectionResult = Field(None)


# Step 7: Description

class Description(BaseModel):
    keywords: List[str] = Field([])
    abstract: str


class DescriptionSectionResult(BaseModel):
    description: Description


class DescriptionSection(BaseModel):
    status: str
    params: Optional[None] = None
    value: Optional[DescriptionSectionResult] = None


# Step 8 Final

class OSTIAuthor(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    affiliation_name: str
    private_email: str
    orcid_id: str
    contributor_type: str


class OSTIRelatedIdentifier(BaseModel):
    related_identifier: str
    relation_type: str
    related_identifier_type: str


class OSTISubmission(BaseModel):
    # REQUIRED
    title: str = Field(...)
    # The dataset publication date, in mm/dd/yyyy, yyyy, or yyyy Month format.
    publication_date: str = Field(...)
    # Primary DOE contract number(s), multiple values may be separated by semicolon.
    contract_nos: str = Field(...)
    # Detailed set of information for person(s) responsible for creation of the dataset
    #  content.Allows transmission of ORCID information and more detailed affiliations
    #  (see below).MAY NOT be used in the same record as the string format, <creators>.
    authors: List[OSTIAuthor] = Field(...)
    # Full URL to the "landing page" for this data set
    site_url: str = Field(...)
    # Type of the main content of the dataset.
    dataset_type: str = Field(...)

    # OPTIONAL
    # The Site Code that owns this particular data set; will default to logged-in user's
    #  primary Site if not set.User must have appropriate privileges to submit records
    #  to this Site.
    site_input_code: str = Field(None)

    # Words or phrases relevant to this data set. Multiple values may be separated by
    #  a semicolon and a following space.
    keywords: str = Field(None)
    # A short description or abstract
    description: str = Field(None)
    # Set of related identifiers for this data
    related_identifiers: List[OSTIRelatedIdentifier] = Field(None)
    # If present, the site-selected DOI inset value for new DOIs.
    doi_infix: str = Field(None)
    # Site specific unique identifier for this data set.
    accession_num: str = Field(None)
    # If credited, the organization name that sponsored / funded the research. For a list
    #  of sponsor organizations, see Sponsoring Organization Authority at
    #  https:#www.osti.gov/elink/authorities.jsp. Multiple codes may be semi-colon delimited.
    sponsor_org: str = Field(None)
    # If credited, the organization name primarily responsible for conducting the research
    originating_research_org: str = Field(None)


class ReviewAndSubmitSectionParams(BaseModel):
    submission: OSTISubmission


class ReviewAndSubmitSectionResult(BaseModel):
    submission: OSTISubmission


class ReviewAndSubmitSection(BaseModel):
    status: str
    params: Optional[ReviewAndSubmitSectionParams] = None
    value: Optional[ReviewAndSubmitSectionResult] = None


# Overall structure

class DOIFormSections(BaseModel):
    narrative: NarrativeSection
    citations: CitationsSection
    orcidLink: ORCIDLinkSection
    authorsImport: AuthorsImportSection
    authors: AuthorsSection
    contracts: ContractsSection
    geolocation: GeolocationSection
    description: DescriptionSection
    reviewAndSubmit: ReviewAndSubmitSection


class DOIApplicationUpdate(BaseModel):
    form_id: str
    sections: DOIFormSections


class InitialDOIApplication(BaseModel):
    sections: DOIFormSections


@router.get("")
async def get_doi_metadata():
    return {
        'description': 'ORCID Link Demo'
    }


@router.post("/doi_application")
async def create_doi_application(
        doi_application: InitialDOIApplication, authorization: str | None = Header(default=None)
):
    db = FileStorage()
    form_id = str(uuid.uuid4())
    application = doi_application.dict(exclude_unset=True)
    application['form_id'] = form_id
    application['owner'] = get_username(authorization)
    application['created_at'] = current_time_millis()
    application['updated_at'] = current_time_millis()
    db.create('doi-forms', form_id, application)
    return application


@router.put("/doi_application")
async def update_doi_application(
        doi_application: DOIApplicationUpdate, authorization: str | None = Header(default=None)
):
    db = FileStorage()
    application_update = doi_application.dict(exclude_unset=True)
    application = db.get('doi-forms', doi_application.form_id)
    application['sections'] = application_update['sections']
    application['updated_at'] = current_time_millis()
    db.update('doi-forms', doi_application.form_id, application)
    return application


@router.get("/doi_application/{form_id}")
async def get_doi_application(
        form_id: str, authorization: str | None = Header(default=None)
):
    db = FileStorage()
    username = get_username(authorization)

    application = db.get('doi-forms', form_id)

    if application['owner'] != username:
        return error_response("auth", "You do not own this application", {})

    return application


@router.delete("/doi_application/{form_id}")
async def delete_doi_application(
        form_id: str, authorization: str | None = Header(default=None)
):
    username = get_username(authorization)

    db = FileStorage()
    application = db.get('doi-forms', form_id)

    if application['owner'] != username:
        return error_response("auth", "You do not own this application", {})

    db.delete('doi-forms', form_id)


@router.get("/doi_applications")
async def get_doi_application(
        authorization: str = Header(...)
):
    username = get_username(authorization)

    db = FileStorage()
    applications = db.list('doi-forms')
    user_applications = [application for application in applications if application['owner'] == username]

    def sorter(app):
        return app['updated_at']

    user_applications.sort(key=sorter, reverse=True)

    return user_applications


# @app.put("/update_narrative_metadata")
# async def update_narrative_metadata(authorization: str | None = Header(default=None)):


@router.get("/osti_contributor_types")
async def get_osti_contributor_types():
    try:
        result = get_json_file('osti-contributor-types')
        return {
            "osti_contributor_types": result
        }
    except Exception as ex:
        return exception_response(ex)
