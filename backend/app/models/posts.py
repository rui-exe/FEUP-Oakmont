from pydantic import BaseModel, validator
from datetime import datetime
from fastapi import HTTPException


class PostBase(BaseModel):
    symbol : str
    text : str
    @validator('text')
    def check_text_length(cls, value):
        if len(value) < 1:
            raise HTTPException(status_code=422, detail="Text must have at least 1 character")
        if len(value) > 500:
            raise HTTPException(status_code=422, detail="Text must have at most 500 characters")
        return value
    
class Post(PostBase):
    timestamp : datetime
    username : str
    