from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database
import secrets

# Example substitutes dictionary
substitutes = {
    "sugar": ["honey", "maple syrup", "agave nectar"],
    "butter": ["margarine", "coconut oil", "olive oil"],
    # Add more substitutes as needed
}

DATABASE_URL = "mysql+mysqlconnector://root:bijubhavan%@localhost:3306/craveit"  # Replace with your actual values

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
    __tablename__ = "users"  # Corrected here
    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(length=100), unique=True, index=True)
    email = Column(String(length=100), unique=True, index=True)
    gender = Column(String(length=20))
    DOB = Column(DateTime)
    password = Column(String(length=200))
    state = Column(String(length=50))
    country = Column(String(length=50))

# Recipe model for SQLAlchemy
class Recipe(Base):
    __tablename__ = "recipes"  # Corrected here
    recipe_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    recipe_name = Column(String(length=255), nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    calories = Column(Integer)

# Ingredients model for SQLAlchemy
class Ingredient(Base):
    __tablename__ = "ingredients"  # Corrected here
    ing_id = Column(Integer, primary_key=True, autoincrement=True)
    ing_name = Column(String(length=100), nullable=False)
    img_url = Column(String(length=255))

# Health Issues model for SQLAlchemy
class HealthIssue(Base):
    __tablename__ = "health_issues"  # Corrected here
    issue_id = Column(Integer, primary_key=True, autoincrement=True)
    issue = Column(String(length=100), nullable=False)

# User Issue model for SQLAlchemy
class UserIssue(Base):
    __tablename__ = "user_issue"  # Corrected here
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, nullable=False)
    issue_id = Column(Integer, ForeignKey("health_issues.issue_id"), primary_key=True, nullable=False)

# Recipe Search History model for SQLAlchemy
class RecipeSearchHistory(Base):
    __tablename__ = "recipe_search_history"  # Corrected here
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    search_term = Column(String(length=255))

# Recipe Issues model for SQLAlchemy
class RecipeIssue(Base):
    __tablename__ = "recipe_issues"  # Corrected here
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id"), primary_key=True, nullable=False)
    issue_id = Column(Integer, ForeignKey("health_issues.issue_id"), primary_key=True, nullable=False)

# Alternative Ingredients model for SQLAlchemy
class AlternativeIngredient(Base):
    __tablename__ = "alternative_ingredients"  # Corrected here
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id"), nullable=False)
    missing_ingredient = Column(String(length=100), nullable=False)
    suggested_ingredient = Column(String(length=100), nullable=False)

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
        from_attributes = True

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
        from_attributes = True

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
        password=hashed_password,  # Corrected field name to 'password'
        state=user.state,
        country=user.country,
    )
    await database.execute(user_data.insert())
    return user_data

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    query = select(User).where(User.email == form_data.username)
    user = await database.fetch_one(query)
    if not user or not verify_password(form_data.password, user.password):
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
        recipe_name=recipe.name,
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

class SubstituteResponse(BaseModel):
    ingredient: str
    substitutes: List[str]

@app.get("/substitutes/{ingredient}", response_model=SubstituteResponse)
async def get_substitutes(ingredient: str):
    substitutes_list = substitutes.get(ingredient, [])
    return SubstituteResponse(ingredient=ingredient, substitutes=substitutes_list)
