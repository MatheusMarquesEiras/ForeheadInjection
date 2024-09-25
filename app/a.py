from infra.actions import init_couses_dev, querry_course_dev, init_database

init_database()
init_couses_dev()
a = querry_course_dev()

print(a)