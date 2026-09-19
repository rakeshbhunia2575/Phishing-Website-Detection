import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    MONGO_URI = os.getenv("MONGO_URI")
