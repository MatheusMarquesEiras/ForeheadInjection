def go_to_page(page, route):
    def route_func(e):
        page.go(route)
    return route_func