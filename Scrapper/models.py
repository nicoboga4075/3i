""" Models for the app """
from pydantic import BaseModel, Field

class FileInfo(BaseModel):
    """ Representation of a file """
    id: str = Field(..., exclude=True)
    name: str
    mimeType: str
    trashed: bool = Field(False, exclude=True)
    parentId: str = Field("", exclude=True)
    parentName: str= Field("")
