
from dotenv import load_dotenv
import os 
from sqlalchemy import create_engine

def get_engine(dbName : str):
    load_dotenv()

    user = os.environ.get("RDSUSER")
    word = os.environ.get("RDSPASS")
    server = os.environ.get("RDSSERV")
    port = os.environ.get("RDSPORT")


    conn_str = f"mssql+pymssql://{user}:{word}@{server}:{port}/{dbName}"

    return create_engine(conn_str, echo=True)


