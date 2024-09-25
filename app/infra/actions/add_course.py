from infra.configs import DBConnector
from infra.entities import Course

def init_couses_dev():
    with DBConnector() as db:
        new1 = Course(name='t1')
        new2 = Course(name='t2')
        new3 = Course(name='t3')
        new4 = Course(name='t4')
        new5 = Course(name='t5')
        new6 = Course(name='t6')
        new7 = Course(name='t7')

        db.session.add_all([new1,new2,new3,new4,new5,new6,new7])
        db.session.commit()