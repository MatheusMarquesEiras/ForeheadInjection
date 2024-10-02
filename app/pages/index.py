import flet as ft
from components import go_to_page
from infra.actions import query_course_dev

def index(page):
    all_courses = query_course_dev()  # Todos os cursos recuperados uma vez

    def search(e):
        # Função de pesquisa que atualiza os cursos exibidos com base no filtro
        filtered_courses = [
            course for course in all_courses if e.control.value.lower() in course[0].lower()
        ]
        update_courses(filtered_courses)

    def update_courses(courses):
        # Limpa os controles atuais e adiciona os cursos filtrados ao GridView
        grid_view.controls.clear()
        grid_view.controls.extend([
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(
                                name=ft.icons.HOME, 
                                size=150, 
                                color=ft.colors.WHITE,
                            ),
                            margin=ft.margin.symmetric(vertical=20, horizontal=0)
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"{course[0]}",
                                size=20,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                text_align=ft.TextAlign.CENTER
                            ),
                            margin=ft.margin.symmetric(vertical=20, horizontal=20),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    spacing=5
                ),
                padding=10,
                alignment=ft.alignment.center,
                bgcolor='#92DBD0',
                border_radius=ft.border_radius.all(5),
                on_click=go_to_page(page, f'/article/{course[1]}')
            ) for course in courses
        ])
        page.update()  # Atualiza a página para refletir as mudanças

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
                padding=ft.padding.symmetric(vertical=0, horizontal=50),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.colors.GREY,
                    offset=ft.Offset(0, 0),
                    blur_style=ft.ShadowBlurStyle.NORMAL,
                ),
            )

    search_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.TextField(
                    hint_text="Digite algo para pesquisar",
                    width=page.width * 0.6,
                    border_radius=20,
                    on_change=search  # Adiciona o listener para a função de busca
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

    # Inicializa com todos os cursos
    update_courses(all_courses)

    content_below_search = ft.Container(
        content=grid_view,
        expand=True,
        alignment=ft.alignment.center,
        margin=ft.margin.symmetric(vertical=10, horizontal=20),
        border=ft.border.all(2, ft.colors.BLACK),
        border_radius=20,
        padding=ft.padding.all(5)
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
