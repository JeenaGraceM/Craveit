from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import secrets

app = FastAPI()

# Configuration for email (add your actual email configuration here)
conf = ConnectionConfig(
    MAIL_USERNAME="your_email@example.com",
    MAIL_PASSWORD="your_password",
    MAIL_FROM="your_email@example.com",
    MAIL_PORT=587,
    MAIL_SERVER="your_smtp_server",
    MAIL_TLS=True,
    MAIL_SSL=False
)

# In-memory data for demo purposes
users_db = {}
recipes_db = {}
substitutes = {
    "eggs": ["flax eggs", "chia eggs"],
    "bacon": ["tempeh", "tofu bacon"],
    "soy sauce": ["coconut aminos"],
    "chicken": ["tofu", "seitan"]
}

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordReset(BaseModel):
    token: str
    new_password: str

class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    dietary: str
    health: Optional[List[str]] = []

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
    expire = datetime.utcnow() + expires_delta
    else:
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
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

@app.post("/register")
async def register_user(user: UserCreate):
    if user.username in users_db:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Username already registered",
    )
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data["hashed_password"] = hashed_password
    users_db[user.username] = user_data
    return {"message": "User registered successfully"}

@app.post("/password-reset-request")
async def password_reset_request(request: PasswordResetRequest):
    for user in users_db.values():
    if user["email"] == request.email:
        reset_token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=10))
        message = MessageSchema(
        subject="Password Reset Request",
        recipients=[request.email],
        body=f"Use this token to reset your password: {reset_token}",
        subtype="html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)
        return {"message": "Password reset email sent"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

@app.post("/password-reset")
async def reset_password(reset: PasswordReset):
    try:
    payload = jwt.decode(reset.token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = get_user(users_db, username)
    if user is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    hashed_password = get_password_hash(reset.new_password)
    users_db[username]["hashed_password"] = hashed_password
    return {"message": "Password reset successfully"}

@app.get("/users/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = get_user(users_db, username)
    if user is None:
    raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/recipes/", response_model=Recipe)
async def add_recipe(recipe: Recipe, token: str = Depends(oauth2_scheme)):
    try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = get_user(users_db, username)
    if user is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_id = len(recipes_db) + 1
    new_recipe = {"id": new_id, **recipe.dict()}
    recipes_db[new_id] = new_recipe
    return new_recipe

@app.get("/recipes/", response_model=List[Recipe])
def get_recipes(ingredients: Optional[List[str]] = Query(None), dietary: Optional[str] = None, health: Optional[List[str]] = Query(None)):
    filtered_recipes = list(recipes_db.values())

    if ingredients:
    filtered_recipes = [recipe for recipe in filtered_recipes if all(ingredient in recipe["ingredients"] for ingredient in ingredients)]

    if dietary:
    filtered_recipes = [recipe for recipe in filtered_recipes if recipe["dietary"] == dietary]

    if health:
    filtered_recipes = [recipe for recipe in filtered_recipes if all(h in recipe["health"] for h in health)]

    # Substitute ingredients according to dietary and health preferences
    for recipe in filtered_recipes:
    for i, ingredient in enumerate(recipe["ingredients"]):
        if ingredient in substitutes:
        recipe["ingredients"][i] = substitutes[ingredient][0]  # Pick the first substitute for simplicity

    return filtered_recipes

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
