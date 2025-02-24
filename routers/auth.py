from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, utils.security
from datetime import timedelta
from jose import JWTError, jwt
from utils.security import SECRET_KEY, ALGORITHM, hash_password, verify_password, create_access_token

router = APIRouter()

# ✅ Fix: Use correct token URL format for FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  

### 🚀 USER REGISTRATION ROUTE ###
@router.post("/register/", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Check if username or email already exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

### 🚀 LOGIN ROUTE ###
@router.post("/login/", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return an access token.
    """
    user = db.query(models.User).filter(
        (models.User.username == form_data.username) | 
        (models.User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # ✅ Generate Token
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=60))

    return {"access_token": access_token, "token_type": "bearer"}

### 🚀 GET CURRENT USER FUNCTION ###
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Extracts the user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    return user

### 🚀 GET CURRENT USER ROUTE ###
@router.get("/me/", response_model=schemas.UserResponse)
def get_me(user: models.User = Depends(get_current_user)):
    """
    Retrieve the currently logged-in user's details.
    Requires a valid JWT token in the Authorization header.
    """
    return user
