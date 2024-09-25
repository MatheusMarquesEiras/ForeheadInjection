from infra.configs import DBConnector
from infra.entities import Course

def querry_course_dev():
    with DBConnector() as db:
        names = [name[0] for name in db.session.query(Course.name).all()]

    return names
