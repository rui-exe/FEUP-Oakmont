from fastapi import APIRouter,Query,Path
from app.api.deps import HBase
from app.crud import posts as posts_crud
from app.models.posts import Post
from datetime import datetime

router = APIRouter()

@router.get("/{posts}")