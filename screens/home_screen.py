import flet as ft
from database import get_user_by_id, get_user_workouts

def HomeScreen(page: ft.Page):
    """
    Cria a tela principal (Fichas de Treino) que o usuário vê após o login.
    """
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/")
        return ft.View()

    user_data = get_user_by_id(user_id)
    username = user_data['username'] if user_data else "Usuário"

    def navigate_to_workout(e):
        """Navega para a tela de treino específica."""
        user_workout_id = e.control.data
        # Armazena o título na sessão para a próxima tela usar
        page.session.set(f"workout_title_{user_workout_id}", e.control.text)
        page.go(f"/workout/{user_workout_id}")

    def logout_clicked(e):
        page.session.clear()
        page.go("/")

    # --- Layout da Tela ---
    workout_buttons = []
    user_workouts = get_user_workouts(user_id)
    for workout in user_workouts:
        workout_buttons.append(
            ft.ElevatedButton(
                text=workout['title'],
                on_click=navigate_to_workout,
                data=workout['user_workout_id'],
                width=300
            )
        )

    return ft.View(
        "/home",
        [
            ft.Column(
                [
                    ft.Text("Fichas de Treino", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Bem-vindo, {username}!", size=18),
                ] + workout_buttons + [
                    ft.TextButton("Sair", on_click=logout_clicked)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
