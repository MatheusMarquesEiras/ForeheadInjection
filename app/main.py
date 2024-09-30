import flet as ft
from pages import index, course
from infra.actions import init_database, init_courses_dev

def main(page: ft.Page):

    def route_change(route):
        if page.route == "/":
            page.views.clear()
            page.views.append(index(page))
        elif page.route.startswith("/article/"):
            course_id = page.route.split("/article/")[1]
            page.views.clear()
            page.views.append(course(page, course_id))
        else:
            page.views.clear()
            page.views.append(index(page))

        page.update()

    page.on_route_change = route_change
    page.theme_mode = "light"

    page.go(page.route if page.route else "/")

if __name__ == "__main__":
    init_database()
    init_courses_dev()
    ft.app(target=main)
