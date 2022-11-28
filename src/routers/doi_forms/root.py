from fastapi import APIRouter
from routers.doi_forms import admin, forms

router = APIRouter(
    prefix="/doi_forms",
    # tags=["items"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

router.include_router(admin.router)
router.include_router(forms.router)


@router.get("")
async def get_doi_forms_root():
    return {
        'status': 'OK'
    }
