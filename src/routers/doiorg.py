import requests
from fastapi import APIRouter
from lib.db import FileStorage
from lib.responses import error_response, exception_response

router = APIRouter(
    prefix="/doi",
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_doi_root():
    return {
        'description': 'Gets DOI stuff'
    }


@router.get("/metadata")
async def get_doi_metadata(
        doi: str
):
    db = FileStorage()
    metadata = db.get('dois', doi)
    if metadata is not None:
        return metadata

    url = f"https://doi.org/{doi}"
    header = {
        'Accept': 'application/vnd.citationstyles.csl+json'
    }
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            metadata = response.json()
            db.create('dois', doi, metadata)
            return metadata
    except Exception as ex:
        raise ValueError('Placeholder error')


@router.get("/citation")
async def get_doi_citation(
        doi: str
):
    url = f"https://doi.org/{doi}"
    header = {
        'Accept': 'text/x-bibliography; style=plos'
    }
    try:
        response = requests.get(url, headers=header)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return {
                "citation": response.text.strip()
            }
        elif response.status_code == 404:
            return error_response(
                'notfound',
                'The supplied DOI was not found',
                data={
                    'doi': doi
                },
                status_code=404,
            )
        else:
            return error_response(
                'unexpected_response',
                'The doi.org service replied with an unexpected response',
                status_code=400,
                data={
                    'status_code': response.status_code
                })
    except Exception as ex:
        return exception_response(ex)
