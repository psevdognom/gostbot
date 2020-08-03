from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Gost(Base):
    __tablename__ = 'gosts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)