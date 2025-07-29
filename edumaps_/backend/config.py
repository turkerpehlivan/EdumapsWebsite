# backend/config.py
import os

class Config:

    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc:///?odbc_connect='
        'DRIVER={ODBC Driver 17 for SQL Server};' 
        'SERVER=.\SQLEXPRESS;'
        'DATABASE=EdumapsDB;'
        'Trusted_Connection=yes;'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False # Performans uyarısını engeller
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cokgizlibirsifre' # Güvenlik için önemli

    # Media Service Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg'}

    # AWS S3 Configuration
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY') or 'test-access-key'
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY') or 'test-secret-key'
    AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME') or 'edumaps-media-test'
    AWS_REGION = os.environ.get('AWS_REGION') or 'eu-central-1'

    # Redis Configuration
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_DB = int(os.environ.get('REDIS_DB') or 0)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # Cache Configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST') or 'localhost'
    CACHE_REDIS_PORT = int(os.environ.get('CACHE_REDIS_PORT') or 6379)
    CACHE_REDIS_DB = int(os.environ.get('CACHE_REDIS_DB') or 0)
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT') or 300)  # 5 minutes