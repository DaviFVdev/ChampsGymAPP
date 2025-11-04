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

        if user_exercise_id_to_replace:
            # Modo de substituição
            replace_exercise_in_workout(user_exercise_id_to_replace, selected_master_id)
        else:
            # Modo de adição
            add_exercise_to_workout(user_workout_id, selected_master_id)

        # Limpa as variáveis de sessão e volta para a tela de treino
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
