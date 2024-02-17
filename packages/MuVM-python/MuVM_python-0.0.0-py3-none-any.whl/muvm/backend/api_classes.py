from pydantic import BaseModel
from typing import Optional, Any, List, Annotated
from fastapi import File, UploadFile, Form, Request


class ImageVariationRequest(BaseModel):
    image: UploadFile = File(...)


class ImageToImageRequest(BaseModel):
    image: Optional[Annotated[bytes, File()]]


class ImageTextToImageRequest(BaseModel):
    image: Optional[Annotated[bytes, File()]]
