import flet as ft
from components.navigation import go_to_page

def course(page):

    def animate_side_bar(e):
        if topics.offset == ft.transform.Offset(0, 0):
            topics.offset = ft.transform.Offset(-2, 0)
        else:
            topics.offset = ft.transform.Offset(0, 0)
        topics.update()

    topics = ft.Container(
        width=250,
        expand=True,
        bgcolor="blue",
        border_radius=10,
        offset=ft.transform.Offset(-2, 0),
        animate_offset=ft.animation.Animation(500),
    )

    nav_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.icons.MENU,
                    icon_color=ft.colors.BLACK,
                    hover_color=ft.colors.WHITE,
                    icon_size=50,
                    on_click=animate_side_bar
                ),
                ft.IconButton(
                    icon=ft.icons.HOME,
                    hover_color='white',
                    icon_color=ft.colors.BLACK,
                    icon_size=50,
                    on_click=go_to_page(page, '/'),
                ),
                ft.IconButton(
                    icon=ft.icons.MAIL,
                    icon_color=ft.colors.BLACK,
                    hover_color=ft.colors.WHITE,
                    icon_size=50,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor="blue",
        height=80,
        alignment=ft.alignment.center,
        border_radius=10,
        padding=ft.padding.symmetric(vertical=0, horizontal=50)
    )

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    """texto""",
                    expand=True,
                    text_align=ft.TextAlign.CENTER,
                    size=20
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ALWAYS,
        ),
        bgcolor=ft.colors.RED,
        expand=True, 
        alignment=ft.alignment.center,
        padding=ft.padding.only(left=80, top=40, right=80),
        border_radius=10,
    )

    return ft.View(
        "/",
            controls=[ 
                nav_bar,
                ft.Stack(
                    controls=[
                        main_content,
                        topics
                    ],
                    expand=True
                )
            ],
            
        
    )