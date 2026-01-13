import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from urllib.parse import quote_plus

load_dotenv()

DATABASE_URL = f"mysql+pymysql://{quote_plus(os.getenv('DB_USERNAME'))}:{quote_plus(os.getenv('DB_PASSWORD'))}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"


engine = create_engine(DATABASE_URL, echo=True)

session = sessionmaker(bind=engine)



def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()