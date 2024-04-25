from app.models.posts import Post
from happybase import Connection
from datetime import datetime
import json

def get_user_posts(db:Connection, username:str,begin:int)->list[Post]:
    """
    Get 10 posts of a user
    """
    user_table = db.table("user")
    posts = []
    for key,data in user_table.row(username.encode("utf-8"),columns=[b"posts"]).items():
        time_stamp = key.decode("utf-8")
        #data is a json
        data = json.loads(data)
        posts.append({
            "username":username,
            "symbol": data["symbol"],
            "timestamp": time_stamp[len("posts:"):],
            "text": data["post"]
        })
    return posts[begin:begin+10]

def get_symbol_posts(db:Connection, symbol:str, begin:int)->list[Post]:
    """
    Get 10 posts of a symbol
    """
    symbol_table = db.table("financial_instruments")
    posts = []
    for key,data in symbol_table.row(symbol.encode("utf-8"),columns=[b"posts"]).items():
        time_stamp = key.decode("utf-8")
        #data is a json
        data = json.loads(data)
        posts.append({
            "username": data["username"],
            "symbol": symbol,
            "timestamp": time_stamp[len("posts:"):],
            "text": data["post"]
        })
    return posts[begin:begin+10]

def create_new_post(db: Connection, post: dict) -> Post:
    """
    Create a new post for a symbol.
    """
    user_table = db.table("user")
    financial_table = db.table("financial_instruments")
    timestamp = datetime.now().isoformat()
    
    post_data = json.dumps({
        "username": post["username"],
        "symbol": post["symbol"],
        "post": post["text"]
    }).encode("utf-8")

    user_post_column = f"posts:{timestamp}".encode("utf-8")
    financial_post_column = f"posts:{timestamp}".encode("utf-8")

    user_batch_data = {
        post["username"].encode("utf-8"): {user_post_column: post_data}
    }

    financial_batch_data = {
        post["symbol"].encode("utf-8"): {financial_post_column: post_data}
    }

    # Open tables and perform batch operations
    with user_table.batch() as user_batch, financial_table.batch() as financial_batch:
        for user_row, user_columns in user_batch_data.items():
            user_batch.put(user_row, user_columns)
        for financial_row, financial_columns in financial_batch_data.items():
            financial_batch.put(financial_row, financial_columns)

    # Update the timestamp in the original post dict
    post["timestamp"] = timestamp
    return post
