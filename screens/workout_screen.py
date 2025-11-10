import flet as ft
from database import get_user_workout_details, get_user_workout_by_id, update_workout
from copy import deepcopy

def WorkoutScreen(page: ft.Page, user_workout_id: int):
    """
    Tela que exibe e permite a edição de uma ficha de treino específica do usuário.
    """
    page.session.set("current_workout_id", user_workout_id)

    # --- Funções de manipulação de dados e navegação ---

    def go_back(e):
        """Volta para a tela principal, limpando o estado de edição."""
        page.session.set("edit_mode", False)
        if page.session.get("workout_in_edit"):
            page.session.remove("workout_in_edit")
        page.go("/home")

    def save_changes(e):
        """Salva as alterações e desativa o modo de edição."""
        if page.session.get("workout_in_edit"):
            edited_data = page.session.get("workout_in_edit")
            update_workout(user_workout_id, edited_data)

        page.session.set("edit_mode", False)
        if page.session.get("workout_in_edit"):
            page.session.remove("workout_in_edit")
        rebuild_view_controls()

    def cancel_changes(e):
        """Cancela as alterações e desativa o modo de edição."""
        page.session.set("edit_mode", False)
        if page.session.get("workout_in_edit"):
            page.session.remove("workout_in_edit")
        rebuild_view_controls()

    def on_title_change(e):
        """Atualiza o título na cópia da sessão."""
        if page.session.get("workout_in_edit"):
            edited_data = page.session.get("workout_in_edit")
            edited_data["details"]['title'] = e.control.value
            page.session.set("workout_in_edit", edited_data)

    def toggle_edit_mode(e):
        """Ativa o modo de edição e atualiza a UI."""
        if not page.session.get("edit_mode"):
            page.session.set("edit_mode", True)

            details_row = get_user_workout_by_id(user_workout_id)
            details_dict = dict(details_row) if details_row else {}
            exercises_rows = get_user_workout_details(user_workout_id)
            exercises_list = [dict(row) for row in exercises_rows]

            workout_copy = {"details": details_dict, "exercises": exercises_list}
            page.session.set("workout_in_edit", deepcopy(workout_copy))

            rebuild_view_controls()

    # --- Controles da UI (definidos uma vez para serem atualizados) ---
    title_control = ft.Text()
    app_bar = ft.AppBar(
        title=title_control,
        leading=ft.IconButton("arrow_back", on_click=go_back),
        actions=[]
    )
    main_content = ft.Column(controls=[], expand=True)

    # --- Função principal para construir e atualizar a UI ---

    def rebuild_view_controls():
        """Reconstrói os controles da view com base no estado atual."""
        is_editing = page.session.get("edit_mode") or False

        def build_exercise_datatable():
            exercises_data = []
            if is_editing and page.session.get("workout_in_edit"):
                exercises_data = page.session.get("workout_in_edit")["exercises"]
            elif not is_editing:
                exercises_data = get_user_workout_details(user_workout_id)

            rows = []
            for ex in exercises_data:
                def create_series_change_handler(user_exercise_id):
                    def on_series_change(e):
                        edited_exercises = page.session.get("workout_in_edit")["exercises"]
                        for item in edited_exercises:
                            if item['user_exercise_id'] == user_exercise_id:
                                item['series'] = e.control.value
                                break
                        page.session.set("workout_in_edit", page.session.get("workout_in_edit"))
                        e.control.border_color = "green"
                        page.update()
                    return on_series_change

                series_control = ft.TextField(
                    value=str(ex['series']),
                    on_submit=create_series_change_handler(ex['user_exercise_id']),
                    width=100
                ) if is_editing else ft.Text(ex['series'])

                action_buttons = []
                if is_editing:
                    def create_move_handler(user_exercise_id, direction):
                        def move_exercise(e):
                            data = page.session.get("workout_in_edit")
                            exercises = data["exercises"]
                            idx = next((i for i, item in enumerate(exercises) if item['user_exercise_id'] == user_exercise_id), -1)
                            if idx != -1:
                                new_idx = idx + direction
                                if 0 <= new_idx < len(exercises):
                                    exercises.insert(new_idx, exercises.pop(idx))
                                    page.session.set("workout_in_edit", data)
                                    rebuild_view_controls()
                        return move_exercise

                    def create_remove_handler(user_exercise_id):
                        def remove_exercise(e):
                            data = page.session.get("workout_in_edit")
                            data["exercises"] = [item for item in data["exercises"] if item['user_exercise_id'] != user_exercise_id]
                            page.session.set("workout_in_edit", data)
                            rebuild_view_controls()
                        return remove_exercise

                    action_buttons = [
                        ft.IconButton("arrow_upward", on_click=create_move_handler(ex['user_exercise_id'], -1)),
                        ft.IconButton("arrow_downward", on_click=create_move_handler(ex['user_exercise_id'], 1)),
                        ft.IconButton("delete", on_click=create_remove_handler(ex['user_exercise_id']), icon_color="red"),
                    ]

                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Row([ft.Text(ex['name'], expand=True)] + action_buttons)),
                    ft.DataCell(series_control),
                ]))

            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Exercício")),
                    ft.DataColumn(ft.Text("Séries"), numeric=True),
                ],
                rows=rows,
                column_spacing=20,
                expand=True,
            )

        # Atualiza o título e as ações
        if is_editing:
            workout_title = page.session.get("workout_in_edit")["details"].get('title', '')
            app_bar.title = ft.TextField(value=workout_title, on_change=on_title_change)
            app_bar.actions = [
                ft.IconButton("save", on_click=save_changes, icon_color="green"),
                ft.IconButton("cancel", on_click=cancel_changes),
            ]
        else:
            workout_data = get_user_workout_by_id(user_workout_id)
            app_bar.title = ft.Text(workout_data['title'] if workout_data else "Treino")
            app_bar.actions = [ft.IconButton("edit", on_click=toggle_edit_mode)]

        # Limpa e reconstrói o conteúdo principal
        main_content.controls.clear()
        main_content.controls.append(build_exercise_datatable())
        if is_editing:
            main_content.controls.append(
                ft.ElevatedButton("Adicionar Exercício", icon="add", on_click=lambda e: page.go("/pick-exercise"))
            )

        page.update()

    # --- Construção Inicial da View ---
    rebuild_view_controls()

    return ft.View(
        f"/workout/{user_workout_id}",
        controls=[main_content],
        appbar=app_bar,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
