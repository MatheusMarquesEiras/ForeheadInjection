import flet as ft
from components.navigation import go_to_page

def index(page):
    # Barra de navegação com uma barra de pesquisa centralizada
    nav_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.TextField(
                    label="Pesquisar...",
                    width=300,  # Ajuste o tamanho da barra de pesquisa aqui
                    border_radius=ft.border_radius.all(20),
                    bgcolor="white",
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor="blue",
        padding=ft.padding.all(10),
        height=50,
    )

    # Corpo da página
    page_content = ft.Column(
        controls=[
            ft.Container(
                content=ft.ElevatedButton("Ir para o artigo", on_click=go_to_page(page, "/article")),
                alignment=ft.alignment.center,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    # Combina tudo em uma visualização
    return ft.View(
        "/",
        controls=[
            nav_bar,         # Barra de navegação com barra de pesquisa
            page_content,    # Conteúdo da página
        ],
    )
