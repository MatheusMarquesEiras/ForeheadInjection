import flet as ft
from pages import index, article
from infra.actions import init_database

def main(page: ft.Page):

    def route_change(route):
        if page.route == "/":
            page.views.clear()
            page.views.append(index(page))
        elif page.route == "/article":
            page.views.clear()
            page.views.append(article(page))
        else:
            page.views.clear()
            page.views.append(index(page))

        page.update()

    page.on_route_change = route_change

    page.go(page.route if page.route else "/")

if __name__ == "__main__":
    init_database()
    ft.app(target=main)
