from fastapi import APIRouter, Body, Path, Query, Depends
from fastapi.exceptions import HTTPException
from Model import device
from typing import List, Annotated
from DataBase import table
from DataBase.base import Session, get_db
from Router import auth


router = APIRouter(prefix="/devices", tags=["Device"])


@router.post("/register")
def register_device(
    user: Annotated[table.Users, Depends(auth.get_current_user)],
    product: device.RegisterDevice=Body(...),
    db: Session = Depends(get_db)
    ):
    '''
    Register Device API

        Register device information
    '''
    pass


@router.delete("/register/{device_id}")
def unregister_device(
    user: Annotated[table.Users, Depends(auth.get_current_user)],
    device_id: int = Path(...),
    db: Session = Depends(get_db)
    ):
    '''
    Unregister Device API

        Unregister device information
    '''
    pass

@router.get("")
def get_device(
    user: Annotated[table.Users, Depends(auth.get_current_user)],
    db: Session = Depends(get_db)
    ):
    '''
    Get Device API

        Get device information
    '''
    pass

@router.get("/all")
def get_all_devices(
    db: Session = Depends(get_db)
    ):
    '''
    Get All Devices API

        Get all device information
    '''
    pass

@router.post("/MQTT/{device_id}")
def mqtt_endpoint(
    device_id: int = Path(...),
    db: Session = Depends(get_db)
    ):
    '''
    MQTT Endpoint API

        先檢查device_id是否有註冊，再進行MQTT連線
        如果device_id沒有註冊，則回傳錯誤訊息
        如果看到topic為"device_name/raw_daa"的訊息，則將訊息存入資料庫
    '''
    pass


