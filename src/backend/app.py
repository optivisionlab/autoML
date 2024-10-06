from fastapi import FastAPI, UploadFile, File, status, HTTPException, Form
import cv2, datetime, os, tempfile, uvicorn, uuid
import numpy as np
from typing import List
from fastapi.responses import JSONResponse
from io import BytesIO
import pandas as pd


# default sync
app = FastAPI()

@app.get("/")
def ping():
    return{
        "AutoML": "version 1.0",
        "message": "Hi there :P"
    }


# @app.post("/login")
# def api_login(username: str = Form(...), password: str = Form(...)):
#     message = "This is Users"
#     if username == "Admin" and password == "Admin":
#         message = "This is Admin"

#     return{
#         "username": username,
#         "password": password,
#         "message": message
#     }


@app.post("/upload-files")
def api_login(files: List[UploadFile] = File(...), mode: str = Form(...), sep: str = Form(...)):
    
    if mode != "csv":
        return{
            "data": None,
            "messages": "File not CSV",
        }

    data_list = []
    files_list = []
    for file in files:
        files_list.append(file.filename)
        contents = file.file.read()
        data = BytesIO(contents)
        df = pd.read_csv(data, on_bad_lines='skip', sep=sep, engine='python')
        data_list.append(df.values.tolist())
        data.close()
        file.file.close()

    return{
        "data_list": data_list,
        "files_list": files_list
    } 


#Nam api user
from users.engine import User
from database.database import get_database
from users.engine import user_helper
from users.engine import users_collection



#Lấy danh sách user
from users.engine import get_list_user
@app.get("/users")
def get_users():
    list_user = get_list_user()
    return list_user

from users.engine import check_exits_username
#Lấy 1 user
@app.get("/users/{username}")
def get_user(username):
    if check_exits_username(username):
        existing_user = users_collection.find_one({"username": username})
        return user_helper(existing_user)
    else:
        return {"message": f"Người dùng {username} không tồn tại"}




from users.engine import checkLogin
@app.post("/login")
def login(username, password):
    if checkLogin(username, password):
        user = users_collection.find_one({"username": username}) 
        if user['role'] == "Admin":
            message = "This is Admin"
        else:
            message = "This is User"
        return {
            "Hello": f"Xin chào {username}",
            "message": message
        }
    else:
        return {"message": "Tài khoản mật khẩu không chính xác!"}



#Thêm user, đăng kí user mới
@app.post("/signup")
def singup(new_user : User):
    if check_exits_username(new_user.username):
        return {"message": f"Người dùng {new_user.username} đã tồn tại"}

    result = users_collection.insert_one(new_user.dict())
    # print(result)
    if result.inserted_id:
        return {'message': f'Đăng ký thành công user: {new_user.username}'}
    else:
        return {'message': 'Đã xảy ra lỗi khi thêm người dùng'}



#Xóa user
@app.delete("/delete/{username}")
def delete_user(username):
    result = users_collection.delete_one({"username": username })
    # print(result)
    if result.deleted_count > 0:
        return {"message": f"Người dùng {username} đã xóa"}
    else:
        return {"message": f"Không thể xóa người dùng {username}. Người dùng không tồn tại hoặc đã xảy ra lỗi"}


#update user
@app.put("/update/{username}")
def update_user(username: str, new_user: User):
    if check_exits_username(username):
        old_user = users_collection.find_one({"username": username})
        new_value = {"$set": new_user.dict()}
        result = users_collection.update_one({"_id": old_user["_id"]},new_value )

        if result.modified_count > 0:
            return {'message': f'Thông tin người dùng {username} đã được cập nhật'}
        else:
            return {'message': f'Không thể cập nhật thông tin người dùng {username}'}
    else:
        return {"message": f"Người dùng {username} không tồn tại"}




if __name__ == "__main__":
    uvicorn.run('app:app', host="127.0.0.1", port=8088, reload=True)
    pass