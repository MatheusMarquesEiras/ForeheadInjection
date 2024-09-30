from infra.configs import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class Course(Base):
    __tablename__ = 'Couses'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    # icon_path = Column(String, nullable=False)

class Topic(Base):
    __tablename__ = 'Topics'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)
    course_reference = Column(Integer, ForeignKey('Couses.id'), nullable=False)

class Content(Base):
    __tablename__ = 'Content'

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    topic_reference = Column(Integer, ForeignKey('Topics.id'), nullable=False)