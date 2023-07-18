from pydantic import BaseModel


class ServiceBaseModel(BaseModel):
    class Config:
        populate_by_name = True
