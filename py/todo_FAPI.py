from fastapi import FastAPI, HTTPException, status
# from contextlib import asynccontextmanager
import sqlite3
import os
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Union
from datetime import datetime
# from bson.objectid import ObjectId
from todo_SQL import db_manager
from dotenv import load_dotenv

db = db_manager()
load_dotenv()

app = FastAPI(title="SQLite Database API", version="1.0.0")
# Pydantic models for request/response
class CreateUser (BaseModel):
    email: EmailStr
    name: str
    password: str
    age: int

class CreateTask (BaseModel):
    email: str
    title: Optional[str] = None
    description: Optional[str] = ""

class UpdateUser (BaseModel):
    old_user_email: EmailStr
    new_user_email: EmailStr
    name: str
    age: int
    created_at: datetime

class UpdateTask (BaseModel):
    email: EmailStr
    task_number: int
    status: int

class DeleteUser (BaseModel):
    email: str
    
class DeleteTask (BaseModel):
    email: EmailStr
    task_number: int
    delete_all: bool

class DisplayUser (BaseModel):
    oid: int
    email: str
    name: str
    age: int
    created_at: datetime
    
class DisplayTask (BaseModel):
    task_number: int
    title: str
    status: str
    description: str
    created_at: datetime

class DisplayUserAll (BaseModel):
    oid: int
    email: str
    name: str
    age: int
    created_at: datetime

@app.get("/")
async def root():
    return {"message": "SQL Database API", "version": "1.0.0"}

# Get all users
@app.get("/users/", response_model = List[DisplayUserAll])
async def get_all_users(ID:Optional[str]=None, 
                        PASSWORD:Optional[str]=None):
    ID = "@!"; PASSWORD = None # DISABLE ADMIN CHECK
    if ID == "@!" and PASSWORD == None:
        users = db.get_all_users()
        return [
            DisplayUserAll(
            oid=user[4],
            email=user[0],
            name=user[1],
            age=user[3],
            created_at=user[5]
            )
            for user in users
        ]
    else:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail = f"Internal server error: Something went wrong"
        )

# Create a new user
@app.post("/users/", response_model = dict, status_code = status.HTTP_201_CREATED)
async def create_user(email: str, #EmailStr
                      name: Optional[str]=None,
                      password: Optional[str]=None,
                      age: Optional[int]=0):
    if name == None:
        name = f"USER_{len(db.get_all_users())+1}"
    if db.get_user(email):
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="✗ User already exists"
        )
    else:
        t=db.create_user(email, name, password, age)
        print(t)
        return {"message": "User created successfully", "user": name}
    
# Get a specific user by email
@app.get("/users/{email}", response_model = DisplayUser)
async def get_user(email: str):
    user = db.get_user(email)
    if not user:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="✗ User not found"
        )
    else:
        return DisplayUser(
            oid=user[0],
            email=user[1],
            name=user[2],
            age=user[3],
            created_at=user[4]
        )
    
# Create a task
@app.post("/todo/", response_model = dict, status_code = status.HTTP_201_CREATED)
async def create_task(email:str, 
                      title:Optional[str] = None, 
                      description:Optional[str] = ""):
# async def create_task(task_input: CreateTask):
#     email=task_input.email
#     title=task_input.title
#     description=task_input.description
    if not db.get_user(email):
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="✗ User not found"
        )
    task = db.create_todo_list(email, title, description)
    if task:
        return {"message": "✓ Post created successfully", "Task #": task}
    else:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="✗ Failed to create post"
        )
    
# Deletes task(s)
@app.delete("/todo/{email}", response_model = dict)
async def delete_task(email:str, 
                      task_number:int,
                      delete_all:Optional[bool] = False):
    if not db.get_users_tasks(email):
        raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "✗ User not found"
        )
    if delete_all == 1:
        db.delete_all_user_task(email)
        return {f"message":"✓ All {email}'s task was deleted"}
    else:
        db.delete_task(email, task_number)
        return {f"message":"✓ {email}'s Task #{task_number} deletion successful"}
    
# Get specific task(s) from user (FOR NOW)
@app.get("/todo/{email}/{task_number}", response_model = List[DisplayTask])
# @app.get("/users/{user_id}/todo", response_model = dict[DisplayTask])
async def get_single_task(email:str,
                        task_number:int = 0,):
    if not db.get_user(email):
        raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "✗ User doesn't exist"
        )
    if not db.get_users_tasks(email):
        raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "✗ User has no task(s)"
        )
    task = db.get_users_tasks(email, task_number)
    print(task)
    return [DisplayTask(
        task_number=task[1],
        title=task[2],
        status=task[3],
        description=task[4],
        created_at=task[5]
        )
    ]
    # if task_number == 0:
    #     tasks = db.get_users_tasks(email)
    #     return [
    #         DisplayTask(
    #         task_number=t[1],
    #         title=t[2],
    #         status=t[3],
    #         description=t[4],
    #         created_at=t[5]
    #         )
    #         for t in tasks
    #     ]
    # else:
    #     # return db.get_users_tasks(email, task_number)
    #     tasks = db.get_users_tasks(email, task_number)
    #     return [
    #         DisplayTask(
    #         task_number=t[1],
    #         title=t[2],
    #         status=t[3],
    #         description=t[4],
    #         created_at=t[5]
    #         )
    #         for t in tasks
    #     ]
    
# Get all tasks from user
@app.get("/todo/{email}", response_model = List[DisplayTask])
async def get_user_todo_all(email:str):
    if not db.get_user(email):
        raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "✗ User doesn't exist"
        )
    if not db.get_users_tasks(email):
        raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "✗ User has no task(s)"
        )
    else:
        tasks = db.get_users_tasks(email)
        return [
            DisplayTask(
            task_number=t[1],
            title=t[2],
            status=t[3],
            description=t[4],
            created_at=t[5]
            )
            for t in tasks
        ]
    
# Deletes user
@app.delete("/users/{email}", response_model = dict)
async def delete_user(email: str):
    if not db.get_user(email):
        raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "✗ User not found"
        )
    else:
        db.delete_all_user_task(email)
        db.delete_user(email)
        return {f"message":f"✓ user {email} deleted"}
    
# Update user info
@app.put("/users/{email}", response_model = dict)
async def update_user(email: str,
                      password: Optional[str]=None,
                      new_email: Optional[str]=None,
                      name: Optional[str]=None,
                      age: Optional[str]=None,):
    user_data = db.get_user(email)
    if not user_data:
        raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "✗ User not found"
        )
    else:
        if new_email == None:
            new_email = email
        if name == None:
            name = user_data[2]
        if age == None:
            age = user_data[3]
        db.update_user_fapi( ### prev work was >>users_collection.update_one<< TO STUDY LATER
            new_email, email, name, age)
        prev_data = user_data
        user_data = db.get_user(new_email)
        if prev_data != user_data:
            return {"User updated successfully": user_data}
        else:
            return {"message": "No changes made to user"}
    
# Update user's task
@app.put("/todo/{email}/{task_number}/status", response_model = dict)
async def update_task_status(email: str,
                      task_number: int,
                      task_status: Optional[bool]=None):
    user_task = db.get_users_tasks(email, task_number)
    # print(task_status)
    if not user_task:
        raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = f"✗ Either user or task #{task_number} not found"
        )
    else:
        if task_status is None:
            task_status = user_task[3]
            return {"message":f"No changes made to user. Task {user_task[1]} is still {user_task[3]}"}
        elif task_status is True:
            task_status = "Complete"
            db.update_task_status(email, task_number, task_status)
            return {"User updated successfully":db.get_users_tasks(email, task_number)}
        else:
            task_status = "Incomplete"
            db.update_task_status(email, task_number, task_status)
            return {"User updated successfully":db.get_users_tasks(email, task_number)}
        
@app.put("/todo/{email}/{task_number}/details", response_model = dict)
async def update_user_task(email: str,
                        #    task_number: int):
                        #    password: str,
                           task_number: int,
                           title: str,
                           t_status: str,
                           description: str):
    user_task = db.get_users_tasks(email, task_number)
    # print("---------",user_task,user_task[3],user_task[4])
    if not user_task:
        raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = f"✗ Either user or task #{task_number} not found"
        )
    else:
        # db.update_user_task(email, task_number, title, task_status, description)
        db.update_user_task(email, task_number, title, t_status, description)
        # db.update_user_task(user_task[0],
        #                     user_task[1],
        #                     user_task[2],
        #                     user_task[3],
        #                     user_task[4])
        return {"message":f"Task details updated"}
    
def execute():
    if os.name == 'nt':
        os.system('cls')  # Windows command to clear the terminal
        # return None
    else:
        os.system('clear')  # Unix-based command (Linux/macOS) to clear the terminal
        # return None
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8001)

if __name__ == "__main__":
    execute()
    # users = db.get_all_users()
    # print(users)