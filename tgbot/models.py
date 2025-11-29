from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


engine = create_engine('sqlite:///gosts.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
#по идеи это все надо вынестии в __init__ файл

class Gost(Base):
    __tablename__ = 'gosts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __str__(self):
        return self.name