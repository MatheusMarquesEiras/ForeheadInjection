import flet as ft
from components.navigation import go_to_page

def index(page):

    def search(e):
        pass

    nav_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.icons.HOME,
                    hover_color='white',
                    icon_color=ft.colors.BLACK,
                    icon_size=50,
                    on_click=go_to_page(page, '/'),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor="blue",
        height=80,
        alignment=ft.alignment.center,
        border_radius=10,
        padding=ft.padding.symmetric(vertical=0, horizontal=50)
    )

    search_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.TextField(
                    hint_text="Digite algo para pesquisar",
                    width=300,
                ),
                ft.ElevatedButton(
                    text="Pesquisar", 
                    on_click=search
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(vertical=10),
    )

    content_below_search = ft.Container(
        content=ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
        ),
        alignment=ft.alignment.center,
        margin=30,
        bgcolor=ft.colors.WHITE,
        expand=True,
        border_radius=10,
        border=ft.border.all(3, ft.colors.BLACK),
    )

    main_content = ft.Column(
        controls=[
            search_container,
            content_below_search,
        ],
        expand=True,
    )

    return ft.View(
        "/",
        controls=[
            nav_bar,
            main_content,
        ],
    )