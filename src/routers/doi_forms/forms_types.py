from typing import List, Optional, Union

from pydantic import BaseModel, Field


#
# Assistance for DOI application persistence.
# Perhaps this can be better thought of as narrative publication metadata,
# which eventually could be stored in the narrative itself.
#

# Section: Select narrative

class StaticNarrativeSummary(BaseModel):
    title: str = Field(...)
    workspaceId: int = Field(...)
    objectId: int = Field(...)
    version: int = Field(...)
    ref: str = Field(...)
    owner: str = Field(...)
    staticNarrativeSavedAt: int = Field(...)
    narrativeSavedAt: int = Field(...)


class NarrativeSectionResult(BaseModel):
    staticNarrative: StaticNarrativeSummary


class NarrativeSection(BaseModel):
    status: str
    params: None = Field(None)
    value: NarrativeSectionResult = Field(None)


# Section: Import citations from narrative and apps

class ImportableCitation(BaseModel):
    doi: Union[str, None] = Field(...)
    url: Union[str, None] = Field(None)
    citation: Union[str, None] = Field(...)
    source: str = Field(...)


class CitationsImportSectionParams(BaseModel):
    staticNarrative: StaticNarrativeSummary


class Citation(BaseModel):
    doi: Union[str, None] = Field(...)
    citation: Union[str, None] = Field(...)
    source: str = Field(...)


class CitationsImportSectionResult(BaseModel):
    citations: List[Citation]


class CitationsImportSection(BaseModel):
    status: str
    params: CitationsImportSectionParams = Field(None)
    value: CitationsImportSectionResult = Field(None)


# Section: add or edit citations.


class CitationsSectionParams(BaseModel):
    citations: List[Citation]


class CitationsSectionResult(BaseModel):
    citations: List[Citation]


class CitationsSection(BaseModel):
    status: str
    params: CitationsSectionParams = Field(None)
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
    staticNarrative: StaticNarrativeSummary


class AuthorsImportSectionResult(BaseModel):
    authors: List[ImportableAuthor] = Field(...)


class AuthorsImportSection(BaseModel):
    status: str
    params: AuthorsImportSectionParams = Field(None)
    value: AuthorsImportSectionResult = Field(None)


# Step 4 - Author

class Author(BaseModel):
    firstName: str = Field(...)
    middleName: str = Field(None)
    lastName: str = Field(...)
    emailAddress: str = Field(...)
    orcidId: str = Field(None)
    institution: str = Field(...)
    contributorType: str = Field(...)


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
    title: str = Field(...)
    keywords: List[str] = Field([])
    abstract: str = Field(...)
    researchOrganization: str = Field(...)


class DescriptionSectionResult(BaseModel):
    description: Description


class DescriptionParams(BaseModel):
    narrativeTitle: str = Field(...)


class DescriptionSection(BaseModel):
    status: str
    params: Optional[DescriptionParams] = None
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
    othnondoe_contract_nos: str | None = Field(None)
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
    # accession_num: str = Field(None)
    # If credited, the organization name that sponsored / funded the research. For a list
    #  of sponsor organizations, see Sponsoring Organization Authority at
    #  https:#www.osti.gov/elink/authorities.jsp. Multiple codes may be semi-colon delimited.
    sponsor_org: str = Field(None)
    # If credited, the organization name primarily responsible for conducting the research
    originating_research_org: str = Field(None)


# Response from OSTI after requesting a DOI
# Notes:
# - site_url not returned
class OSTIRecord(OSTISubmission):
    hidden: str = Field(...)
    osti_id: str = Field(...)
    status: str = Field(...)
    related_resource: str | None = Field(None)
    product_nos: str | None = Field(None)
    product_type: str = Field(...)
    other_identifying_numbers: str | None = Field(None)
    availability: str | None = Field(None)
    collaboration_names: str | None = Field(None)
    language: str = Field(...)
    country: str = Field(...)
    subject_categories_code: str | None = Field(None)
    # Should be static narrative ref? wsid/version or wsid.version
    accession_num: str | None = Field(...)
    # Note string "none" if pending
    date_first_submitted: str = Field(...)
    date_last_submitted: str = Field(...)
    entry_date: str = Field(...)
    doi: str = Field(...)
    doi_status: str = Field(...)
    file_extension: str | None = Field(None)
    # should be web browser?
    software_needed: str | None = Field(None)
    dataset_size: str | None = Field(None)
    contact_name: str = Field(...)
    contact_org: str = Field(...)
    contact_email: str = Field(...)
    # NB the leading "@" replaced with "_" for Python class compatibility
    _status: str = Field(...)
    _released: str = Field(...)


class ReviewAndSubmitSectionParams(BaseModel):
    submission: OSTISubmission


class ReviewAndSubmitSectionResult(BaseModel):
    requestId: str = Field(...)


class ReviewAndSubmitSection(BaseModel):
    status: str
    params: Optional[ReviewAndSubmitSectionParams] = None
    value: Optional[ReviewAndSubmitSectionResult] = None


# Overall structure

class DOIFormSections(BaseModel):
    narrative: NarrativeSection
    description: DescriptionSection
    orcidLink: ORCIDLinkSection
    authorsImport: AuthorsImportSection
    authors: AuthorsSection
    citationsImport: CitationsImportSection
    citations: CitationsSection
    contracts: ContractsSection
    # geolocation: GeolocationSection
    reviewAndSubmit: ReviewAndSubmitSection


class DOIApplicationUpdate(BaseModel):
    form_id: str
    sections: DOIFormSections
    status: str


class InitialDOIApplication(BaseModel):
    sections: DOIFormSections
    status: str


class DOIFormRecord(BaseModel):
    form_id: str = Field(...)
    status: str = Field(...)
    owner: str = Field(...)
    created_at: int = Field(...)
    updated_at: int = Field(...)
    sections: DOIFormSections = Field(...)


class PostDOIRequestParams(BaseModel):
    form_id: str = Field(...)
    submission: OSTISubmission = Field(...)


class GetDOIRequestParams(BaseModel):
    doi: str = Field(None)
    # osti_id: str = Field(None)


class GetDOIRequestResult(BaseModel):
    record: OSTIRecord
    _start: str = Field(...)
    _rows: str = Field(...)
    _numFound: str = Field(...)


class GetDOIRequestResponse(BaseModel):
    result: GetDOIRequestResult
