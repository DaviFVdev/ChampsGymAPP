import flet as ft
from database import get_user_workout_details, update_exercise_series, remove_exercise_from_workout, get_user_workout_by_id

def WorkoutScreen(page: ft.Page, user_workout_id: int):
    """
    Tela que exibe e permite a edição de uma ficha de treino específica do usuário.
    """
    page.session.set("current_workout_id", user_workout_id)

    def toggle_edit_mode(e):
        """Ativa ou desativa o modo de edição."""
        edit_mode = not page.session.get("edit_mode")
        page.session.set("edit_mode", edit_mode)
        page.go(f"/workout/{user_workout_id}") # Recarrega a página para refletir o novo modo

    def go_back(e):
        page.session.remove("edit_mode")
        page.go("/home")

    def build_exercise_datatable():
        """Constrói a DataTable com base nos exercícios do workout."""
        exercises = get_user_workout_details(user_workout_id)
        rows = []
        is_editing = page.session.get("edit_mode") or False

        for ex in exercises:
            series_control = ft.Text(ex['series'])
            if is_editing:
                def on_series_change(e, user_exercise_id=ex['user_exercise_id']):
                    update_exercise_series(user_exercise_id, e.control.value)
                    e.control.border_color = "green"
                    page.update()

                series_control = ft.TextField(
                    value=ex['series'],
                    on_submit=lambda e, uei=ex['user_exercise_id']: on_series_change(e, uei),
                    width=100
                )

            action_buttons = []
            if is_editing:
                def replace_click(e, user_exercise_id=ex['user_exercise_id']):
                    page.session.set("exercise_to_replace", user_exercise_id)
                    page.go("/pick-exercise")

                def remove_click(e, user_exercise_id=ex['user_exercise_id']):
                    remove_exercise_from_workout(user_exercise_id)
                    page.go(f"/workout/{user_workout_id}") # Recarrega

                action_buttons = [
                    ft.IconButton("swap_horiz", on_click=lambda e, uei=ex['user_exercise_id']: replace_click(e, uei)),
                    ft.IconButton("delete", on_click=lambda e, uei=ex['user_exercise_id']: remove_click(e, uei), icon_color="red")
                ]

            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Row([ft.Text(ex['name'])] + action_buttons)),
                ft.DataCell(series_control),
            ]))

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Exercício")),
                ft.DataColumn(ft.Text("Séries")),
            ],
            rows=rows,
            expand=True
        )

    # --- Layout da Tela ---
    workout_data = get_user_workout_by_id(user_workout_id)
    workout_title = workout_data['title'] if workout_data else "Treino Detalhes"

    edit_mode_active = page.session.get("edit_mode") or False

    add_button = ft.ElevatedButton(
        "Adicionar Exercício",
        icon="add",
        on_click=lambda e: page.go("/pick-exercise")
    ) if edit_mode_active else ft.Container()

    return ft.View(
        f"/workout/{user_workout_id}",
        [
            ft.AppBar(
                title=ft.Text(workout_title),
                leading=ft.IconButton("arrow_back", on_click=go_back),
                actions=[
                    ft.IconButton(
                        "check" if edit_mode_active else "edit",
                        on_click=toggle_edit_mode,
                        icon_color="green" if edit_mode_active else None
                    )
                ]
            ),
            build_exercise_datatable(),
            add_button
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
