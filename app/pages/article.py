import flet as ft
from components.navigation import go_to_page

def article(page):
    # Barra de navegação com uma barra de pesquisa centralizada
    nav_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.TextField(
                    label="Pesquisar...",
                    width=300,  # Ajuste o tamanho da barra de pesquisa aqui
                    border_radius=ft.border_radius.all(20),
                    bgcolor="white"
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # Alinhamento ao centro
        ),
        bgcolor="blue",
        padding=ft.padding.all(10),
        height=50, 
    )

    # Corpo da página
    page_content = ft.Column(
        controls=[
            ft.Container(
                content=ft.ElevatedButton("Ir para home", on_click=go_to_page(page, "/")),
                alignment=ft.alignment.center,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    return ft.View(
        "/",
        controls=[
            nav_bar,
            page_content,
        ],
    )
