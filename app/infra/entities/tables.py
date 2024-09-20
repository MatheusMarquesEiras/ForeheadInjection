from infra.configs import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class Couse(Base):
    __tablename__ = 'Couses'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    icon_path = Column(String, nullable=False)

class Topic(Base):
    __tablename__ = 'Topics'

    id = Column(Integer, primary_key=True)
    sequence = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    cource_reference = Column(Integer, ForeignKey('Couses.id'), nullable=False)