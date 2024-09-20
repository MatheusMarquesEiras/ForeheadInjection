from infra.configs import Base, DBConnector

def init_database():
    with DBConnector() as db:
        Base.metadata.create_all(db.session.bind)