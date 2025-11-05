import flet as ft
from database import get_all_master_exercises, replace_exercise_in_workout, add_exercise_to_workout

def ExercisePickerScreen(page: ft.Page):
    """
    Tela para selecionar um exercício da biblioteca mestre.
    """
    # Parâmetros passados pela rota
    user_workout_id = page.session.get("current_workout_id")
    user_exercise_id_to_replace = page.session.get("exercise_to_replace")

    def select_exercise(e):
        """Callback para quando um exercício é selecionado."""
        selected_master_id = e.control.data
        selected_exercise_name = e.control.title.value # Pega o nome do ListTile

        if user_exercise_id_to_replace:
            # Modo de substituição: Atualiza a cópia na sessão
            edited_data = page.session.get("workout_in_edit")
            for ex in edited_data["exercises"]:
                if ex['user_exercise_id'] == user_exercise_id_to_replace:
                    ex['master_exercise_id'] = selected_master_id
                    ex['name'] = selected_exercise_name # Atualiza o nome para UI
                    break
            page.session.set("workout_in_edit", edited_data)
        else:
            # Modo de adição: Adiciona à cópia na sessão
            edited_data = page.session.get("workout_in_edit")
            new_exercise = {
                # ID temporário negativo para novos exercícios, para evitar conflitos
                'user_exercise_id': - (len(edited_data["exercises"]) + 1),
                'master_exercise_id': selected_master_id,
                'name': selected_exercise_name,
                'series': '3x10' # Padrão para novos exercícios
            }
            edited_data["exercises"].append(new_exercise)
            page.session.set("workout_in_edit", edited_data)

        # Limpa a variável de substituição e volta
        if page.session.contains_key("exercise_to_replace"):
            page.session.remove("exercise_to_replace")
        page.go(f"/workout/{user_workout_id}")

    def go_back(e):
        """Volta para a tela de treino sem fazer alterações."""
        page.session.remove("exercise_to_replace")
        page.go(f"/workout/{user_workout_id}")

    # --- Layout da Tela ---
    all_exercises = get_all_master_exercises()
    exercise_list = ft.ListView(expand=True, spacing=10)

    for group, exercises in all_exercises.items():
        exercise_list.controls.append(
            ft.Text(group, size=20, weight=ft.FontWeight.BOLD)
        )
        for ex in exercises:
            exercise_list.controls.append(
                ft.ListTile(
                    title=ft.Text(ex['name']),
                    data=ex['master_exercise_id'],
                    on_click=select_exercise,
                )
            )

    return ft.View(
        "/pick-exercise",
        [
            ft.AppBar(
                title=ft.Text("Selecione um Exercício"),
                leading=ft.IconButton("arrow_back", on_click=go_back),
            ),
            exercise_list
        ]
    )
