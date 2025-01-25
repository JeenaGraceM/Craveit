from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
import secrets

DATABASE_URL = "mysql+mysqlconnector://root:Annajacob005%@localhost:3306/craveit"  

# SQLAlchemy specific code
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

database = Database(DATABASE_URL)

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model for SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=100), unique=True, index=True)
    email = Column(String(length=100), unique=True, index=True)
    gender = Column(String(length=20))
    dob = Column(DateTime)
    hashed_password = Column(String(length=200))
    state = Column(String(length=50))
    country = Column(String(length=50))

# Recipe model for SQLAlchemy
class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=100))
    ingredients = Column(String(length=500))
    dietary = Column(String(length=50))
    health = Column(String(length=100))
    user_id = Column(Integer)

# Create database tables
Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    username: str
    email: str
    gender: str
    dob: datetime
    password: str
    state: str
    country: str

class UserBase(BaseModel):
    id: int
    username: str
    email: str
    gender: str
    dob: datetime
    state: str
    country: str

    class Config:
        orm_mode = True

class RecipeCreate(BaseModel):
    name: str
    ingredients: List[str]
    dietary: str
    health: Optional[List[str]] = []

class RecipeBase(BaseModel):
    id: int
    name: str
    ingredients: List[str]
    dietary: str
    health: Optional[List[str]] = []
    user_id: int

    class Config:
        orm_mode = True

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/register", response_model=UserBase)
async def register_user(user: UserCreate):
    query = select(User).where(User.email == user.email)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    hashed_password = get_password_hash(user.password)
    user_data = User(
        username=user.username,
        email=user.email,
        gender=user.gender,
        dob=user.dob,
        hashed_password=hashed_password,
        state=user.state,
        country=user.country,
    )
    await database.execute(user_data.insert())
    return user_data

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    query = select(User).where(User.email == form_data.username)
    user = await database.fetch_one(query)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserBase)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    query = select(User).where(User.username == username)
    user = await database.fetch_one(query)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/recipes/", response_model=RecipeBase)
async def add_recipe(recipe: RecipeCreate, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    query = select(User).where(User.username == username)
    user = await database.fetch_one(query)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    recipe_data = Recipe(
        name=recipe.name,
        ingredients=",".join(recipe.ingredients),
        dietary=recipe.dietary,
        health=",".join(recipe.health) if recipe.health else None,
        user_id=user.id
    )
    await database.execute(recipe_data.insert())
    return recipe_data

@app.get("/recipes/", response_model=List[RecipeBase])
async def get_recipes(ingredients: Optional[List[str]] = Query(None), dietary: Optional[str] = None, health: Optional[List[str]] = Query(None)):
    query = select(Recipe)
    if ingredients:
        for ingredient in ingredients:
            query = query.where(Recipe.ingredients.like(f"%{ingredient}%"))
    if dietary:
        query = query.where(Recipe.dietary == dietary)
    if health:
        for h in health:
            query = query.where(Recipe.health.like(f"%{h}%"))

    recipes = await database.fetch_all(query)
    return recipes

@app.get("/substitutes/{ingredient}", response_model=List[str])
def get_substitutes(ingredient: str, dietary: Optional[str] = None, health: Optional[List[str]] = Query(None)):
    substitutes_list = substitutes.get(ingredient, ["No substitutes available"])

    if dietary or health:
        # Filter substitutes according to dietary and health preferences
        filtered_substitutes = []
        for substitute in substitutes_list:
            # Check if substitute meets dietary and health preferences (here we assume all substitutes are suitable, but you can add more logic)
            filtered_substitutes.append(substitute)
        return filtered_substitutes

    return substitutes_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
