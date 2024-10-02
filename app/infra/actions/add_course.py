from infra.configs import DBConnector
from infra.entities import Course, Topic, Content

def init_courses_dev():
    with DBConnector() as db:

        newc1 = Course(name='mat')
        newc2 = Course(name='lab')
        newc3 = Course(name='py')
        newc4 = Course(name='js')
        newc5 = Course(name='ts')
        newc6 = Course(name='lua')
        newc7 = Course(name='c++')

        db.session.add_all([newc1, newc2, newc3, newc4, newc5, newc6, newc7])
        db.session.commit()

        newt1 = Topic(name='linear', sequence=0, course_reference=newc1.id)
        newt2 = Topic(name='geometria', sequence=1, course_reference=newc1.id)
        newt3 = Topic(name='cos x', sequence=2, course_reference=newc1.id)
        newt4 = Topic(name='sen x', sequence=3, course_reference=newc1.id)
        newt5 = Topic(name='tan x', sequence=4, course_reference=newc1.id)
        newt6 = Topic(name='financial', sequence=5, course_reference=newc1.id)
        newt7 = Topic(name='sum', sequence=6, course_reference=newc1.id)

        db.session.add_all([newt1, newt2, newt3, newt4, newt5, newt6, newt7])
        db.session.commit()

        newco1 = Content(content='algebra linear é usada para ...', topic_reference=newt1.id)
        newco2 = Content(content='geometria é usada para ...', topic_reference=newt2.id)
        newco3 = Content(content='cos x é usado para ...', topic_reference=newt3.id)
        newco4 = Content(content='sen x é usado para ...', topic_reference=newt4.id)
        newco5 = Content(content='tan x é usado para ...', topic_reference=newt5.id)
        newco6 = Content(content='financeiro é usado para ...', topic_reference=newt6.id)
        newco7 = Content(content='somatorio é usado para ...', topic_reference=newt7.id)

        db.session.add_all([newco1, newco2, newco3, newco4, newco5, newco6, newco7])
        db.session.commit()
