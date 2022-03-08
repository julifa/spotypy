from sqlalchemy import TIMESTAMP, Column, StringColumn

from sqlacl import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from spoty_etl.cfg import DB_CONNSTR

engine = create_engine(DB_CONNSTR) if DB_CONNSTR else None
meta = MetaData(engine)
Base = declarative_base(metadata=meta)

TABLENAME = "history"

class SpotipyOutput(Base):
    __tablename__ = TABLENAME

    played_at= Column(TIMESTAMP, primary_key=True)
    artist= Column(String(255), nullable=False)
    track= Column(String(255), nullable=False)