import flet as ft
from components.navigation import go_to_page

def index(page):
    def search(e):
        print("Search initiated")

    def create_items():
        return [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=ft.icons.HOME, size=30, color=ft.colors.WHITE),
                        ft.Text(
                            f"Este é o texto do Item {i + 1}. Ele pode ser bem longo e precisa ser truncado se ultrapassar duas linhas.",
                            size=16,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                padding=10,
                alignment=ft.alignment.center,
                bgcolor='#D7C0D0',
                border_radius=ft.border_radius.all(5),
                on_click=go_to_page(page, '/article')
            ) for i in range(20)
        ]

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
        bgcolor="#77BA99",
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
                    width=page.width * 0.6,
                    border_radius=20,
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Pesquisar", 
                        on_click=search,
                        width=page.width * 0.15,
                        height=page.height * 0.05,
                        style=ft.ButtonStyle(
                            text_style=ft.TextStyle(size=20)
                        )
                    ),
                    padding=ft.padding.only(top=20),
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(vertical=20),
    )


    grid_view = ft.GridView(
        expand=True,
        runs_count=4,
        max_extent=400,
        spacing=10,
        run_spacing=10,
        padding=10,
        child_aspect_ratio=1.0,
    )

    grid_view.controls.extend(create_items())

    content_below_search = ft.Container(
        content=grid_view,
        expand=True,
        alignment=ft.alignment.center,
        margin=30,
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
        bgcolor='#EFF0D1'
    )