# api/auth.py - Système d'authentification JWT avec FastAPI

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
import os

# ===== CONFIGURATION =====
SECRET_KEY = os.getenv("SECRET_KEY", "votre-cle-secrete-super-longue-et-aleatoire-changez-moi-en-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB
MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
MONGO_URI = f"mongodb://{MONGO_HOST}:27017/"
client = MongoClient(MONGO_URI)
db = client["crypto_db"]
users_collection = db["users"]

# Password hashing (utilise argon2 si bcrypt pose problème)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ===== MODÈLES PYDANTIC =====

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str
    created_at: datetime
    is_active: bool = True
    role: str = "user"  # "user" ou "admin"

class UserResponse(UserBase):
    created_at: datetime
    is_active: bool
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# ===== FONCTIONS UTILITAIRES =====

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie le mot de passe."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash le mot de passe."""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[dict]:
    """Récupère un utilisateur depuis MongoDB."""
    return users_collection.find_one({"username": username})

def get_user_by_email(email: str) -> Optional[dict]:
    """Récupère un utilisateur par email."""
    return users_collection.find_one({"email": email})

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authentifie un utilisateur."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ===== DÉPENDANCES =====

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Récupère l'utilisateur actuel depuis le token JWT."""
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
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Vérifie que l'utilisateur est actif."""
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: dict = Depends(get_current_active_user)) -> dict:
    """Vérifie que l'utilisateur est admin."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# ===== FONCTIONS DE CRÉATION D'UTILISATEUR =====

def create_user(user: UserCreate) -> dict:
    """Crée un nouvel utilisateur."""
    # Vérifier si l'utilisateur existe déjà
    if get_user(user.username):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    if get_user_by_email(user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Créer l'utilisateur
    user_dict = {
        "username": user.username,
        "email": user.email,
        "hashed_password": get_password_hash(user.password),
        "created_at": datetime.utcnow(),
        "is_active": True,
        "role": "user"
    }
    
    result = users_collection.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    return user_dict