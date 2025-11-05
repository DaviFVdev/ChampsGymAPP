import flet as ft
from database import get_user_workout_details, get_user_workout_by_id, update_workout
from copy import deepcopy

def WorkoutScreen(page: ft.Page, user_workout_id: int):
    """
    Tela que exibe e permite a edição de uma ficha de treino específica do usuário.
    """
    page.session.set("current_workout_id", user_workout_id)

    def toggle_edit_mode(e):
        """Ativa ou desativa o modo de edição, criando uma cópia temporária dos dados."""
        edit_mode = not page.session.get("edit_mode")
        page.session.set("edit_mode", edit_mode)

        if edit_mode:
            # Carrega os dados originais e armazena uma cópia na sessão
            original_workout = {
                "details": get_user_workout_by_id(user_workout_id),
                "exercises": get_user_workout_details(user_workout_id)
            }
            page.session.set("workout_in_edit", deepcopy(original_workout))
        else:
            # Se sair do modo de edição (ex: clicando no checkmark), salva
            save_changes(e)

        page.go(f"/workout/{user_workout_id}")

    def go_back(e):
        """Volta para a tela principal, limpando o estado de edição."""
        try:
            page.session.remove("edit_mode")
            page.session.remove("workout_in_edit")
        except KeyError:
            pass
        page.go("/home")

    def save_changes(e):
        """Salva as alterações feitas no modo de edição."""
        if page.session.get("workout_in_edit"):
            edited_data = page.session.get("workout_in_edit")
            update_workout(user_workout_id, edited_data)

        # Limpa o estado de edição
        try:
            page.session.remove("edit_mode")
            page.session.remove("workout_in_edit")
        except KeyError:
            pass
        page.go(f"/workout/{user_workout_id}")

    def cancel_changes(e):
        """Cancela as alterações feitas no modo de edição."""
        try:
            page.session.remove("edit_mode")
            page.session.remove("workout_in_edit")
        except KeyError:
            pass
        page.go(f"/workout/{user_workout_id}")


    def build_exercise_list():
        """Constrói a lista de exercícios, com drag-and-drop se em modo de edição."""
        is_editing = page.session.get("edit_mode") or False

        if is_editing:
            exercises = page.session.get("workout_in_edit")["exercises"]
        else:
            exercises = get_user_workout_details(user_workout_id)

        exercise_widgets = []

        def on_drag_accept(e):
            src_id = int(e.src_id)
            dest_id = int(e.control.data)

            edited_data = page.session.get("workout_in_edit")
            exercise_list = edited_data["exercises"]

            src_index = next((i for i, item in enumerate(exercise_list) if item['user_exercise_id'] == src_id), -1)
            dest_index = next((i for i, item in enumerate(exercise_list) if item['user_exercise_id'] == dest_id), -1)

            if src_index != -1 and dest_index != -1:
                moved_item = exercise_list.pop(src_index)
                exercise_list.insert(dest_index, moved_item)
                page.session.set("workout_in_edit", edited_data)
                page.update()


        for ex in exercises:
            series_control = ft.Text(ex['series'])
            if is_editing:
                def on_series_change(e, user_exercise_id=ex['user_exercise_id']):
                    edited_exercises = page.session.get("workout_in_edit")["exercises"]
                    for item in edited_exercises:
                        if item['user_exercise_id'] == user_exercise_id:
                            item['series'] = e.control.value
                            break
                    page.session.set("workout_in_edit", page.session.get("workout_in_edit"))
                    e.control.border_color = "green"
                    page.update()

                series_control = ft.TextField(
                    value=str(ex['series']),
                    on_submit=lambda e, uei=ex['user_exercise_id']: on_series_change(e, uei),
                    width=100
                )

            action_buttons = []
            if is_editing:
                def replace_click(e, user_exercise_id=ex['user_exercise_id']):
                    page.session.set("exercise_to_replace", user_exercise_id)
                    page.go("/pick-exercise")

                def remove_click(e, user_exercise_id=ex['user_exercise_id']):
                    edited_data = page.session.get("workout_in_edit")
                    edited_data["exercises"] = [item for item in edited_data["exercises"] if item['user_exercise_id'] != user_exercise_id]
                    page.session.set("workout_in_edit", edited_data)
                    page.update()

                action_buttons = [
                    ft.IconButton("swap_horiz", on_click=lambda e, uei=ex['user_exercise_id']: replace_click(e, uei)),
                    ft.IconButton("delete", on_click=lambda e, uei=ex['user_exercise_id']: remove_click(e, uei), icon_color="red"),
                    ft.Icon("drag_handle")
                ]

            exercise_card = ft.Card(
                content=ft.ListTile(
                    title=ft.Text(ex['name']),
                    subtitle=series_control,
                    trailing=ft.Row(action_buttons)
                )
            )

            if is_editing:
                draggable_widget = ft.Draggable(
                    group="exercises",
                    content=exercise_card,
                )
                exercise_widgets.append(ft.DragTarget(
                    group="exercises",
                    content=draggable_widget,
                    on_accept=on_drag_accept,
                    data=ex['user_exercise_id']
                ))
            else:
                exercise_widgets.append(exercise_card)

        return ft.Column(controls=exercise_widgets)

    # --- Layout da Tela ---
    edit_mode_active = page.session.get("edit_mode") or False

    if edit_mode_active:
        workout_title = page.session.get("workout_in_edit")["details"]['title']
    else:
        workout_data = get_user_workout_by_id(user_workout_id)
        workout_title = workout_data['title'] if workout_data else "Treino Detalhes"

    def on_title_change(e):
        # Atualiza o título na cópia da sessão
        edited_data = page.session.get("workout_in_edit")
        edited_data["details"]['title'] = e.control.value
        page.session.set("workout_in_edit", edited_data)

    title_control = ft.TextField(value=workout_title, on_change=on_title_change) if edit_mode_active else ft.Text(workout_title)

    add_button = ft.ElevatedButton(
        "Adicionar Exercício",
        icon="add",
        on_click=lambda e: page.go("/pick-exercise")
    ) if edit_mode_active else ft.Container()

    app_bar_actions = []
    if edit_mode_active:
        app_bar_actions = [
            ft.IconButton("save", on_click=save_changes, icon_color="green"),
            ft.IconButton("cancel", on_click=cancel_changes),
        ]
    else:
        app_bar_actions = [
            ft.IconButton("edit", on_click=toggle_edit_mode),
        ]

    return ft.View(
        f"/workout/{user_workout_id}",
        controls=[
            ft.AppBar(
                title=title_control,
                leading=ft.IconButton("arrow_back", on_click=go_back),
                actions=app_bar_actions
            ),
            build_exercise_list(),
            add_button
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
