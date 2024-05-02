from fastapi import APIRouter, HTTPException, Path

from app.crud import posts as crud_posts
from app.api.deps import HBase, CurrentUser
from app.models.posts import PostBase
router = APIRouter()

@router.get("/{username}/{id}")
def get_post_by_id(db: HBase, id: int, username: str = Path(..., title="The username of the user")):
    """
    Get the post with the provided id and username.
    """
    return crud_posts.get_post_by_id_versions(db=db, username=username, id=id)


@router.put("/{id}")
def edit_post(db: HBase, id: int, post: PostBase, current_user: CurrentUser):
    """
    Edit the post with the provided id and username.
    """
    post_data = {
        "username": current_user.username,
        "symbol": post.symbol,
        "text": post.text,
        "post_id": id
    }
    crud_posts.edit_post(db, post_data)