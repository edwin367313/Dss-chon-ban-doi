import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]  # tới thư mục backend/
load_dotenv(ROOT_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "DSS Mate API")
APP_PORT = int(os.getenv("APP_PORT", "5000"))

SQL_ODBC_DRIVER = os.getenv("SQL_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")
SQL_SERVER = os.getenv("SQL_SERVER", "localhost\\SQLEXPRESS")
SQL_DATABASE = os.getenv("SQL_DATABASE", "DSS Mate")
SQL_TRUSTED_CONNECTION = os.getenv("SQL_TRUSTED_CONNECTION", "yes")

SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
