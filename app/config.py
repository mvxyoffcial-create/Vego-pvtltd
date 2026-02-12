from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str
    DATABASE_NAME: str = "veggo_db"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # Email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    FROM_NAME: str = "VegGo Platform"
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: str
    
    # Delivery Fee (Can be updated by admin)
    BASE_DELIVERY_FEE: float = 50
    PRICE_PER_KM: float = 10
    PRICE_PER_METER: float = 0.01
    
    # App
    FRONTEND_URL: str = "http://localhost:3000"
    ORDER_CANCEL_TIME_MINUTES: int = 5
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
