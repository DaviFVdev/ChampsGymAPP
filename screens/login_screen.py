import flet as ft

def LoginScreen(page: ft.Page):
    """
    Cria a tela de login.
    """
    # --- Controles da UI ---
    email_field = ft.TextField(label="E-mail ou nome de usuário", width=300)
    password_field = ft.TextField(label="Senha", password=True, width=300)
    error_text = ft.Text(value="", color="red")

    def login_clicked(e):
        """Função chamada ao clicar no botão de login."""
        # A lógica de autenticação será implementada futuramente.
        # Por enquanto, apenas exibimos uma mensagem.
        error_text.value = "Funcionalidade de login ainda não implementada."
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
                    email_field,
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
