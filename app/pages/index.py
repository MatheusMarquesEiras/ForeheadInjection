import flet as ft
from components.navigation import go_to_page

def index(page):
    # Barra de navegação com uma barra de pesquisa centralizada
    nav_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.icons.HOME,
                    hover_color='white',
                    icon_size=60,
                    icon_color=ft.colors.BLACK,
                    width=200,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor="blue",
        height=80,  
        alignment=ft.alignment.center 
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
