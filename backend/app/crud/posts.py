from app.models.posts import Post
from happybase import Connection
import time
import datetime
import json
import struct

MAX_LONG = 2**63 - 1

def number_to_java_long(number):
    java_long = struct.pack('>q', number)
    return java_long 
def java_long_to_number(java_long):
    # Unpack the Java long to a signed 64-bit integer
    number = struct.unpack('>q', java_long)[0]
    return number

def increment_byte_array(byte_array:bytes):
    #convert the byte array to a binary number
    number = int.from_bytes(byte_array, "big")
    #increment the number
    number += 1
    #convert the number back to a byte array
    return number.to_bytes(len(byte_array), "big")

def get_user_posts(db:Connection, username:str,begin:int)->list[Post]:
    """
    Get 10 posts of a user
    """
    user_table = db.table("user")
    posts = []
    for _,row in user_table.scan(row_start=username.encode("utf-8"), row_stop=increment_byte_array(username.encode("utf-8")), columns=[b"posts"], sorted_columns=True):
        for column,data in row.items():
            data = json.loads(data)
            time_reverse_ms = java_long_to_number(column[len("posts:"):])
            time_ms = MAX_LONG-time_reverse_ms
            posts.append({
                "username":username,
                "symbol": data["symbol"],
                "timestamp": datetime.datetime.fromtimestamp(int(time_ms/1000)),
                "text": data["post"]
            })
        break
    return posts[begin:begin+10]

def get_symbol_posts(db:Connection, symbol:str, begin:int)->list[Post]:
    """
    Get 10 posts of a symbol
    """
    symbol_table = db.table("financial_instruments")
    posts = []
    for _,row in symbol_table.scan(row_start=symbol.encode("utf-8"), row_stop=increment_byte_array(symbol.encode("utf-8")), columns=[b"posts"], sorted_columns=True):
        for column,data in row.items():
            data = json.loads(data)
            time_reverse_ms = java_long_to_number(column[len("posts:"):])
            time_ms = MAX_LONG-time_reverse_ms
            posts.append({
                "username":data["username"],
                "symbol": symbol,
                "timestamp": datetime.datetime.fromtimestamp(int(time_ms/1000)),
                "text": data["post"]
            })
        break
    return posts[begin:begin+10]

def create_new_post(db: Connection, post: dict) -> Post:
    """
    Create a new post for a symbol.
    """
    user_table = db.table("user")
    financial_table = db.table("financial_instruments")
    timestamp = int(round(time.time() * 1000))
    timestamp = MAX_LONG - timestamp
    timestamp = number_to_java_long(timestamp)
    
    #get last post id from the symbol_post table counter and increment it that is saved in this symbol_table.counter_set(b'info', b'post_id', post_id)
    symbol_posts_table = db.table("symbol_posts")
    post_id = symbol_posts_table.counter_inc(b"info", b"info:post_id", 1)

    post_data = json.dumps({
        "username": post["username"],
        "symbol": post["symbol"],
        "post": post["text"],
        "post_id": post_id,
    }).encode("utf-8")

    user_post_column = b"posts:" + timestamp
    financial_post_column = b"posts:" + timestamp

    user_batch_data = {
        post["username"].encode("utf-8"): {user_post_column: post_data}
    }

    financial_batch_data = {
        post["symbol"].encode("utf-8"): {financial_post_column: post_data}
    }

    data_posts_by_symbol = dict()
    data_posts_by_user = dict()
    #create the post_id_symbol and post_id_user columns
    data_posts_by_symbol[f"{post['symbol']}_{post_id}"] = {b'posts:' + timestamp: post_data}
    data_posts_by_user[f"{post['username']}_{post_id}"] = {b'posts:' + timestamp: post_data}

    # save the table of the user_posts
    user_posts_table = db.table("user_posts")

    # save the words of the post in the letters table
    letters_table = db.table("letters")
    post_text = post["text"].split()
    #remove ponctuation
    post_text = [word.strip(",.!?") for word in post_text]
    #remove enters
    post_text = [word.replace('\n','') for word in post_text]

    letters = dict()
    for word in post_text:
        if word not in letters:
            letters[word] = {}
        letters[word] = {f"posts:{post['username']}_{post_id}": b"1"}
        letters[word][f"posts:{post['symbol']}_{post_id}"] = b"1"



    # Open tables and perform batch operations
    with user_table.batch() as user_batch, financial_table.batch() as financial_batch, symbol_posts_table.batch() as symbol_posts_batch, user_posts_table.batch() as user_posts_batch:
        for user_row, user_columns in user_batch_data.items():
            user_batch.put(user_row, user_columns)
        for financial_row, financial_columns in financial_batch_data.items():
            financial_batch.put(financial_row, financial_columns)
        for symbol_row, symbol_columns in data_posts_by_symbol.items():
            symbol_posts_batch.put(symbol_row.encode("utf-8"), symbol_columns)
        for user_row, user_columns in data_posts_by_user.items():
            user_posts_batch.put(user_row.encode("utf-8"), user_columns)
        for word, word_columns in letters.items():
            letters_table.put(word.encode("utf-8"), word_columns)

    # Update the timestamp in the original post dict
    post["timestamp"] = timestamp
    return post

def search_symbol_posts(db:Connection, symbol:str,phrase:str) -> list[Post]:
    """
    Search the posts of a symbol by phrase
    """
    #split the phrase into words and get the posts where all the words appear 
    words_table = db.table("letters")
    posts = []
    posts_ids = set()
    for word in phrase.split():
        #acces the row of the word in the table the word is the rowkey
        row = words_table.row(word.encode("utf-8"))
        #if the word is not in the table continue
        if not row:
            return []
        #get the posts where the word appears
        word_posts_id = set()
        for column,data in row.items():
            if column.decode("utf-8").startswith(f"posts:{symbol}_"):
                word_posts_id.add(column)
        # imtersect the posts of the word with the posts of the other words
        if not posts_ids:
            posts_ids = word_posts_id
        else:
            posts_ids = posts_ids.intersection(word_posts_id)
                    
    #get the posts from the symbol_posts table the key is post_id_symbol and the post is in the columns posts:value
    symbol_posts_table = db.table("symbol_posts")
    for post_id in posts_ids:
        post_id = post_id.decode("utf-8")
        symbol_id = post_id.split("_")[1]
        post_row = symbol_posts_table.row(f"{symbol}_{symbol_id}".encode("utf-8"))
        for column, post in post_row.items():
            post = json.loads(post)
            time_reverse_ms = java_long_to_number(column[len("posts:"):])
            time_ms = MAX_LONG-time_reverse_ms

            posts.append({
                "username":post["username"],
                "symbol": symbol,
                "timestamp": datetime.datetime.fromtimestamp(int(time_ms/1000)),
                "text": post["post"]
            })
    #sort the posts by timestamp
    posts.sort(key=lambda x: x["timestamp"], reverse=True)

    return posts
    
def search_user_posts(db:Connection, username:str, phrase:str) -> list[Post]:
    """
    Search the posts of a user by phrase
    """
    #split the phrase into words and get the posts where all the words appear 
    words_table = db.table("letters")
    posts = []
    posts_ids = set()
    for word in phrase.split():
        #acces the row of the word in the table the word is the rowkey
        row = words_table.row(word.encode("utf-8"))
        #if the word is not in the table continue
        if not row:
            return []
        #get the posts where the word appears
        word_posts_id = set()
        for column,data in row.items():
            if column.decode("utf-8").startswith(f"posts:{username}_"):
                word_posts_id.add(column)
        # imtersect the posts of the word with the posts of the other words
        if not posts_ids:
            posts_ids = word_posts_id
        else:
            posts_ids = posts_ids.intersection(word_posts_id)
                    
    #get the posts from the user_posts table the key is post_id_user and the post is in the columns posts:value
    user_posts_table = db.table("user_posts")
    for post_id in posts_ids:
        post_id = post_id.decode("utf-8")
        user_id = post_id.split("_")[1]
        post_row = user_posts_table.row(f"{username}_{user_id}".encode("utf-8"))
        for column, post in post_row.items():
            post = json.loads(post)
            time_reverse_ms = java_long_to_number(column[len("posts:"):])
            time_ms = MAX_LONG-time_reverse_ms

            posts.append({
                "username":username,
                "symbol": post["symbol"],
                "timestamp": datetime.datetime.fromtimestamp(int(time_ms/1000)),
                "text": post["post"]
            })

    #sort the posts by timestamp
    posts.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return posts
