import flet as ft
from functions import search_arxiv, semantic_sort

def main(page: ft.Page):
    page.title = "Semantic arXiv Search"
    page.scroll = "auto"
    page.window.width = 900
    page.window.height = 850

    results_column = ft.Column()

    def handle_submit(e):
        query = text_input.value.strip()
        results_column.controls.clear()

        if query:
            loading_text = ft.Text("Searching ...", color=ft.Colors.GREY_300, size=17)
            results_column.controls.append(loading_text)
            page.update()

            try:
                articles = search_arxiv(query, 30)
                sorted_articles = semantic_sort(query, articles)

                results_column.controls.clear()

                if sorted_articles:
                    for article in sorted_articles[:10]:
                        results_column.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(article['title'], weight="bold", color=ft.Colors.WHITE, size=19),
                                    ft.TextButton(
                                        text=article['url'],
                                        url=article['url'],
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.BLUE_300,
                                            padding=0,
                                            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_300),
                                            text_style=ft.TextStyle(size=16),
                                        )
                                    ),
                                    ft.Text(f"Similarity: {article['score']:.4f}", color=ft.Colors.GREY_400, size=16),
                                    ft.Text(f"Published: {article['published'].date()}", color=ft.Colors.GREY_400, size=16),
                                    ft.Text(f"Citations: {article['citations']}", color=ft.Colors.GREY_400, size=16),
                                    ft.TextField(
                                        value=article['generated_summary'],
                                        read_only=True,
                                        multiline=True,
                                        border=None,
                                        filled=False,
                                        text_style=ft.TextStyle(color=ft.Colors.GREY_300, size=16),
                                    )

                                ]),
                                padding=10,
                                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                                border_radius=10
                            )
                        )
                else:
                    results_column.controls.append(ft.Text("No results found.", color=ft.Colors.GREY_300))
            except Exception as ex:
                results_column.controls.append(ft.Text(f"Error - {ex}; enter a new query", color=ft.Colors.RED))
                print(f"Error during search: {ex}")
        page.update()

    text_input = ft.TextField(
        label="Enter arXiv query",
        on_submit=handle_submit,
        autofocus=True,
        expand=True,
        text_style=ft.TextStyle(color=ft.Colors.WHITE, size=20),
    )

    send_button = ft.ElevatedButton(
        text="Submit",
        on_click=handle_submit,
            style=ft.ButtonStyle(
        text_style=ft.TextStyle(size=15))
    )

    page.add(
        ft.Text("Semantic arXiv Search", size=35, weight="bold", color=ft.Colors.WHITE),
        ft.Row([text_input, send_button]),
        results_column
    )

ft.app(target=main)
