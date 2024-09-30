from infra.configs import DBConnector
from infra.entities import Course, Topic  

def query_course_dev():
    with DBConnector() as db:
        courses = [name for name in db.session.query(Course.name, Course.id).all()]

    return courses

def query_topic_dev(id):
    with DBConnector() as db:
        topics = [topic for topic in db.session.query(Topic.name, Topic.id).where(Topic.course_reference == id)]
    
    return topics

