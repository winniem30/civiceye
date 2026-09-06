from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.db.models import User
from pydantic import BaseModel, EmailStr

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str = "citizen"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
