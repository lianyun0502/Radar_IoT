from fastapi import APIRouter, Body, Path, Query, Depends
from fastapi.exceptions import HTTPException
from Model import user
from typing import List, Annotated
from DataBase import table
from DataBase.base import Session, get_db
from uuid import uuid4
from passlib.context import CryptContext
from Router import auth


router = APIRouter(prefix="/users", tags=["User"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("", response_model=user.OutUser)
async def create_user(user: user.CreateUser=Body(...), 
                      db: Session = Depends(get_db)):
    '''
    Create User API

        透過 body 傳入使用者資訊，並進行註冊

    '''
    if db.query(table.Users).filter(table.Users.id == user.id).scalar():
        raise HTTPException(status_code=400, detail="User already registered")
    user.password = pwd_context.hash(user.password)
    db.add(table.Users(**user.model_dump()))
    db.commit()
    return user

@router.delete("", response_model=user.OutUser)
async def delete_user(
    user: Annotated[table.Users, Depends(auth.get_current_user)],
    db: Session = Depends(get_db)):
    '''
    Delete User API

        刪除使用者資訊
    '''
    db.delete(user)
    db.commit()
    return user

@router.get("", response_model=user.OutUser)
async def get_user(
    user: Annotated[table.Users, Depends(auth.get_current_user)], 
    db: Session = Depends(get_db)):
    '''
    Get User API

        取得登入使用者資訊
    '''
    return user

@router.get("/all", response_model=List[user.OutUser])
async def get_all_users(db: Session = Depends(get_db)):
    '''
    Get All Users API

        取得所有註冊的使用者資訊
    '''
    users = db.query(table.Users).all()
    return users

