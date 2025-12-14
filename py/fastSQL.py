from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import sqlite3
from sql_database import DatabaseManager

app = FastAPI(title = "SQLite Database API", version = "1.0.0")

# Pydantic models for request/response
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int

class UserResponse(BaseModel) :
    id: int
    name: str
    email: str
    age: int
    created_at: str

class PostCreate(BaseModel):
    user_id: int
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: str

class PostResponseForUser(BaseModel) :
    id: int
    title: str
    content: str
    created_at: str

# Initialize database
db = DatabaseManager ( )

@app.get("/")
async def root():
    return {"message": "SQLite Database API", "version": "1.0.0"}

@app.post("/users/", response_model = dict, status_code = status.HTTP_201_CREATED)
async def create_user(user: UserCreate): #Create a new user"""
    try:
        user_id = db.create_user(user.name, user.email, user.age)
        if user_id:
            return {"message": "User created successfully", "user_id": user_id}
        else:
            raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Failed to create user. Email might already exist."
            )

    except Exception as e:
        raise HTTPException(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail = f"Internal server error: {str(e)}"
        )
    
@app.get("/users/", response_model = List[UserResponse])
async def get_all_users(): # Gets everyone
    try:
        users = db.get_all_users()
        return [
            UserResponse(
                id = user_i[0],
                name = user_i[1],
                email = user_i[2],
                age = user_i[3],
                created_at = user_i[4],
            )
            for user_i in users
        ]
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Internal server err: {str(err)}"
        )
    
@app.get("/users/{user_id}", response_model = UserResponse)
async def get_user(user_id: int): # Get use by specific ID
    try:
        with sqlite3.connect(db.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User N/A"
            )
        return UserResponse(
            id = user[0],
            name = user[1],
            email = user[2],
            age = user[3],
            created_at = user[4],
        )

    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Internal server err: {str(err)}"
        )
    
@app.post("/posts/", response_model = dict, status_code = status.HTTP_201_CREATED)
async def create_post(post: PostCreate): # Create new post/record
    try:
        with sqlite3.connect(db.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT id FROM users WHERE id = ?", (post.user_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    stauts_code = status.HTTP_404_NOT_FOUND,
                    detail  = "User N/A"
                )
        post_id = db.create_post(post.user_id, post.title, post.content)
        if post_id:
            return {"message": "Post created successfully", "post_id": post_id}
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Failed to create post/record"
                )
            
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detial = f"Internal server err: {str(err)}"
        )

@app.get("/users/{user_id}/posts", response_model = List[PostResponseForUser])
async def get_user_posts(user_id: int): # Gets post/record by specific ID
    try:
        with sqlite3.connect(db.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = "User N/A"
                )
        posts = db.get_user_posts(user_id)
        return [
            PostResponseForUser(
                id = post_i[0],
                name = post_i[1],
                email = post_i[2],
                age = post_i[3],
                created_at = post_i[4],
            )
            for post_i in posts
        ]

    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Internal server err: {str(err)}"
        )
    
@app.get("/posts/", response_model = List[PostResponse])
async def get_user(user_id: int): # Gets all post/record
    try:
        with sqlite3.connect(db.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
            posts = cursor.fetchone()
        return [
            UserResponse(
                id = post_i[0],
                name = post_i[1],
                email = post_i[2],
                age = post_i[3],
                created_at = post_i[4],
            )
            for post_i in posts
        ]

    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Internal server err: {str(err)}"
        )
    
@app.delete("/users/{user_id}", response_model = dict)
async def delete_user(user_id: int): # Deletes a user and their post/records
    try:
        with sqlite3.connect(db.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = "User N/A"
                )
        success = db.delete_user(user_id)
        if success:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Failed to create post/record"
                )

    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Internal server err: {str(err)}"
        )
    
@app.delete("/posts/{post_id}", response_model = dict)
async def delete_user(post_id: int): # Deletes a specific post/records
    try:
        with sqlite3.connect(db.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = "Post/Record N/A"
                )
        return {"message": "Post/Record deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Internal server err: {str(err)}"
        )
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000)