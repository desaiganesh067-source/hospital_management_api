import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")


if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")

if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL is not set in .env")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in .env")