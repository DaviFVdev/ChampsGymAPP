import flet as ft
from database import verify_user

def LoginScreen(page: ft.Page):
    """
    Cria a tela de login.
    """
    # --- Controles da UI ---
    identifier_field = ft.TextField(label="E-mail ou nome de usuário", width=300)
    password_field = ft.TextField(label="Senha", password=True, width=300)
    error_text = ft.Text(value="", color="red")

    def login_clicked(e):
        """Função chamada ao clicar no botão de login."""
        identifier = identifier_field.value.strip()
        password = password_field.value

        if not identifier or not password:
            error_text.value = "Preencha todos os campos."
            page.update()
            return

        user_id = verify_user(identifier, password)

        if user_id:
            # Limpa a tela e armazena o user_id na sessão
            page.session.set("user_id", user_id)
            error_text.value = ""
            identifier_field.value = ""
            password_field.value = ""
            page.go('/home')
        else:
            error_text.value = "Usuário ou senha inválidos."
            page.update()


    def go_to_register(e):
        """Redireciona para a tela de cadastro."""
        page.go('/register')

    # --- Layout da Tela ---
    return ft.View(
        "/",
        [
            ft.Column(
                [
                    ft.Text("Champs Gym App", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text("Bem-vindo de volta!", size=18),
                    identifier_field,
                    password_field,
                    ft.ElevatedButton("Entrar", on_click=login_clicked),
                    error_text,
                    ft.TextButton("Não tem uma conta? Registre-se", on_click=go_to_register)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
