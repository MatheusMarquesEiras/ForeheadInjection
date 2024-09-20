from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DBConnector:
    def __init__(self):
        self.url = 'postgresql+psycopg2://root:root@localhost:5432/data_db'
        self.engine = create_engine(
            url=self.url
        )
        self.session_factory = sessionmaker(bind=self.engine,
                                            expire_on_commit=False)
        self.session = None
    
    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()