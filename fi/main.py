import flet as ft
from pages import index, article

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
            page.views.append(index(page))  # Rota padrão

        page.update()

    # Configurando o evento de mudança de rota
    page.on_route_change = route_change

    # Definindo a rota inicial
    page.go(page.route if page.route else "/")

# Iniciando o app na porta 8000
ft.app(target=main)
