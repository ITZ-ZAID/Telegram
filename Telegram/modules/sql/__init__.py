from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from Telegram import DB_URI, ZInit, log


def start() -> scoped_session:
    engine = create_engine(DB_URI, client_encoding="utf8", echo=ZInit.DEBUG)
    log.info("[PostgreSQL] Fetching Database Details......")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
try:
    SESSION: scoped_session = start()
except Exception as e:
    log.exception(f'[PostgreSQL] Failed to connect due to {e}')
    exit()
   
log.info("[PostgreSQL] Database Connected .")
