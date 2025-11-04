import flet as ft
from database import init_db, get_user_workouts
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.home_screen import HomeScreen
from screens.workout_screen import WorkoutScreen
from screens.exercise_picker_screen import ExercisePickerScreen

def main(page: ft.Page):
    """
    Função principal que configura e executa o aplicativo Flet.
    """
    # --- Configuração da Página/Janela ---
    page.title = "Champs Gym App"
    page.window_width = 400
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.DARK # Tema escuro

    # --- Inicialização do Banco de Dados ---
    init_db()

    # --- Gerenciamento de Rotas ---
    def route_change(route):
        """
        Altera a view (tela) da página com base na rota atual.
        """
        page.views.clear()
        if page.route == "/":
            page.views.append(LoginScreen(page))
        elif page.route == "/register":
            page.views.append(RegisterScreen(page))
        elif page.route == "/home":
            # Proteção de rota: só permite acesso se o user_id estiver na sessão
            if not page.session.get("user_id"):
                page.go("/")
            else:
                page.views.append(HomeScreen(page))
        elif page.route == "/pick-exercise":
            if not page.session.get("user_id"):
                page.go("/")
            else:
                page.views.append(ExercisePickerScreen(page))
        # Rota dinâmica para as telas de treino do usuário
        elif page.route.startswith("/workout/"):
            if not page.session.get("user_id"):
                page.go("/")
            else:
                parts = page.route.split("/")
                user_workout_id = int(parts[2])
                # Precisamos do título, que está na home screen. Vamos buscá-lo na sessão por simplicidade.
                workout_title = page.session.get(f"workout_title_{user_workout_id}", "Treino")
                page.views.append(WorkoutScreen(page, user_workout_id, workout_title))

        page.update()

    def view_pop(view):
        """
        Chamado quando o usuário clica no botão "voltar" do Flet.
        """
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # --- Inicia o app na rota raiz ---
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)
