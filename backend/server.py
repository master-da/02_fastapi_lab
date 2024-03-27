from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import re

uri = "mongodb+srv://mdnokib2000:FjQRoHlzq7gKyZtA@ip-lab.y4pic.mongodb.net/?retryWrites=true&w=majority&appName=ip-lab"

client = MongoClient(uri, server_api=ServerApi('1'))
db = client["registration_db"]
users_collection = db["users"]

# FastAPI app instance
app = FastAPI()

# Configure CORS middleware
origins = [
    "http://localhost:3000",  # Replace with the origin(s) you want to allow
    # Add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRegistration(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone_number: str

    # Validator for username
    @validator('username')
    def validate_username(cls, value):
        if len(value) < 6:
            raise ValueError("Username must be at least 6 characters long")
        return value

    # Validator for password
    @validator('password')
    def validate_password(cls, value):
        if len(value) < 7:
            raise ValueError("Password must be at least 7 characters long")
        return value

    # Validator for phone number
    @validator('phone_number')
    def validate_phone_number(cls, value):
        if not re.match(r'^\d{11}$', value):
            raise ValueError("Phone number must be exactly 11 digits long")
        return value
        
# Route for user registration
@app.post("/register")
async def register_user(user_data: UserRegistration):
    
    print(user_data)
    
    # Check if username already exists
    if users_collection.count_documents({"username": user_data.username}, limit=1):
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    if users_collection.count_documents({"email": user_data.email}, limit=1):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Check if phone number already exists
    if users_collection.count_documents({"phone_number": user_data.phone_number}, limit=1):
        raise HTTPException(status_code=400, detail="Phone number already exists")

    # Save user data to MongoDB
    user_data = user_data.dict()
    users_collection.insert_one(user_data)

    return {"message": "User registered successfully"}