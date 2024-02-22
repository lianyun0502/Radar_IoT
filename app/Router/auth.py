from fastapi import Depends, HTTPException, status, APIRouter
from DataBase.base import Session, get_db
from DataBase import table
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from Model import auth


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(prefix="/auth", tags=["Auth"])


# 401 Unauthorized 相同的錯誤訊息，所以提取出來，這邊是驗證使用者身份失敗
incorret_user_or_password:HTTPException = HTTPException(
    status_code=401,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

# 401 Unauthorized 相同的錯誤訊息，所以提取出來，這邊是驗證token失敗
credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_password(plain_password:str, hashed_password:str)->bool:
    '''驗證hash密碼'''
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(user_id:str, password:str, db:Session)->table.Users:
    '''驗證使用者身份'''
    user = db.query(table.Users).filter(table.Users.id == user_id).scalar()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(password, user.password):
        raise incorret_user_or_password
    return user

def get_user(user_id:str, db:Session)->table.Users:
    '''取得使用者資訊'''
    user = db.query(table.Users).filter(table.Users.id == user_id).scalar()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta])->str:
    '''建立 JWT token'''
    to_encode = data.copy()

    # 設定 token timeout
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    '''取得當前使用者'''
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = auth.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(user_id=token_data.username, db=db)
    return user


@router.post("/token", response_model=auth.Token, summary="登入", description="透過使用者id和密碼登入")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    '''
    登入 API

        透過 form 傳入使用者id和密碼, 並驗證使用者身份後回傳 JWT token 作為登入憑證
    '''
    user = authenticate_user(form_data.username, form_data.password, db=db)
    access_token = create_access_token(
        data={"sub": user.id}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return auth.Token(access_token=access_token, token_type="bearer")

@router.get("/users/items/")
async def read_own_items(current_user: Annotated[table.Users, Depends(get_current_user)]):
    '''
        測試用
    '''
    return [{"item_id": "Foo", "owner": current_user.id}]
