import flet as ft
from database import get_user_by_id

def HomeScreen(page: ft.Page):
    """
    Cria a tela principal (Fichas de Treino) que o usuário vê após o login.
    """
    # --- Verificação de Sessão ---
    user_id = page.session.get("user_id")
    if not user_id:
        # Se não há usuário na sessão, redireciona para o login
        page.go("/")
        return ft.View() # Retorna uma view vazia para evitar renderizar esta tela

    user_data = get_user_by_id(user_id)
    username = user_data['username'] if user_data else "Usuário"

    def workout_button_clicked(e):
        """Função placeholder para os botões de treino."""
        page.snack_bar = ft.SnackBar(ft.Text(f"Botão '{e.control.text}' clicado!"), open=True)
        page.update()

    def logout_clicked(e):
        """Limpa a sessão e redireciona para a tela de login."""
        page.session.clear()
        page.go("/")

    # --- Layout da Tela ---
    return ft.View(
        "/home",
        [
            ft.Column(
                [
                    ft.Text("Fichas de Treino", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Bem-vindo, {username}!", size=18),
                    ft.ElevatedButton("Treino A = Peito e Triceps", on_click=workout_button_clicked, width=300),
                    ft.ElevatedButton("Treino B = Quadriceps", on_click=workout_button_clicked, width=300),
                    ft.ElevatedButton("Treino C = Costas e Biceps", on_click=workout_button_clicked, width=300),
                    ft.ElevatedButton("Treino D = Ombro e Posterior", on_click=workout_button_clicked, width=300),
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
