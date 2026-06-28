import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000/api")
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_jwt_key") # Same as Backend
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "credentials/firebase-adminsdk.json")

# Cache Settings
CACHE_TTL = int(os.getenv("CACHE_TTL", "600")) # 10 minutes default

# Streamlit App settings
APP_NAME = "Analytics BI"
APP_VERSION = "1.0.0"
