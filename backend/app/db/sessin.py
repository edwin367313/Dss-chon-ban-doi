import pyodbc
from backend.app.Core import Config

def _conn_str() -> str:
    # Windows Auth
    if (Config.SQL_TRUSTED_CONNECTION or "").lower() in ("yes", "true", "1"):
        return (
            f"DRIVER={{{Config.SQL_ODBC_DRIVER}}};"
            f"SERVER={Config.SQL_SERVER};"
            f"DATABASE={Config.SQL_DATABASE};"
            f"Trusted_Connection=yes;"
        )
    # SQL Auth
    return (
        f"DRIVER={{{Config.SQL_ODBC_DRIVER}}};"
        f"SERVER={Config.SQL_SERVER};"
        f"DATABASE={Config.SQL_DATABASE};"
        f"UID={Config.SQL_USERNAME};PWD={Config.SQL_PASSWORD};"
    )

def get_conn():
    return pyodbc.connect(_conn_str())
