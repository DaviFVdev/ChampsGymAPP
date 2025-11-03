import flet as ft
from database import init_db
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.home_screen import HomeScreen
from screens.workout_screen import WorkoutScreen
from data.workouts import WORKOUT_DATA

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
        # Rota dinâmica para as telas de treino
        elif page.route in WORKOUT_DATA:
            if not page.session.get("user_id"):
                page.go("/")
            else:
                workout_info = WORKOUT_DATA[page.route]
                page.views.append(WorkoutScreen(page, workout_info))
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
