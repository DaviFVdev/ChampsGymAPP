import flet as ft

def WorkoutScreen(page: ft.Page, workout_data: dict):
    """
    Cria uma view de treino genérica com base nos dados fornecidos.
    """
    def go_back(e):
        """Navega de volta para a tela principal."""
        page.go("/home")

    # --- Criação da Tabela de Exercícios ---
    # (Por enquanto, as linhas estarão vazias, conforme solicitado)
    exercise_rows = []
    for exercise in workout_data.get("exercises", []):
        exercise_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(exercise.get("name"))),
                    ft.DataCell(ft.Text(exercise.get("series"))),
                ]
            )
        )

    exercise_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Exercício")),
            ft.DataColumn(ft.Text("Séries")),
        ],
        rows=exercise_rows,
        expand=True
    )

    # --- Layout da Tela ---
    return ft.View(
        route=page.route, # Usa a rota atual para a view
        controls=[        # <--- A correção é aqui
            ft.AppBar(
                leading=ft.IconButton("arrow_back", on_click=go_back),
                title=ft.Text(workout_data.get("title", "Treino"))
            ),
            ft.Container(
                content=exercise_table,
                padding=10
            )
        ]
    )
