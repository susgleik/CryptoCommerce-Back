from pydantic_settings import BaseSettings
from typing import Optional, List
import os 

class Settings(BaseSettings):
    # Database settings for local dev
    #database_url: str
    
    # Database settings for azure
    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: int = 3306
    database_url: str
    
    # security 
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30
    
     # SMTP Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "your-email@gmail.com"
    smtp_password: str = "your-app-password"
    
    # CORS settings
    allowed_origins: str = "*"
    allowed_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    allowed_headers: str = "*"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"
        
# Create a global settings instance
settings = Settings()