from pydantic import BaseModel
from datetime import datetime

class Post(BaseModel):
    username : str
    symbol : str
    text : str
    timestamp : datetime
    