""" Models for the app """

from pydantic import BaseModel, Field

class FileInfo(BaseModel):
    id: str= Field(..., exclude=True)
    name: str
    mimeType: str
