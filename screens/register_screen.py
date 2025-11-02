import flet as ft
from database import add_user

def RegisterScreen(page: ft.Page):
    """
    Cria a tela de cadastro.
    """
    # --- Controles da UI ---
    username_field = ft.TextField(label="Nome de usuário", width=300)
    email_field = ft.TextField(label="E-mail", width=300)
    password_field = ft.TextField(label="Senha", password=True, width=300)
    error_text = ft.Text(value="", color="red")

    def register_clicked(e):
        """Função chamada ao clicar no botão de registrar."""
        username = username_field.value.strip()
        email = email_field.value.strip()
        password = password_field.value

        if not username or not email or not password:
            error_text.value = "Todos os campos são obrigatórios."
            page.update()
            return

        success = add_user(username, email, password)

        if success:
            # Limpa os campos e redireciona para o login
            username_field.value = ""
            email_field.value = ""
            password_field.value = ""
            error_text.value = ""
            page.snack_bar = ft.SnackBar(ft.Text("Cadastro realizado com sucesso!"), open=True)
            page.go('/')
        else:
            error_text.value = "Nome de usuário ou e-mail já existe."
            page.update()

    def go_to_login(e):
        """Redireciona para a tela de login."""
        page.go('/')

    # --- Layout da Tela ---
    return ft.View(
        "/register",
        [
            ft.Column(
                [
                    ft.Text("Crie sua conta", size=30),
                    username_field,
                    email_field,
                    password_field,
                    ft.ElevatedButton("Cadastrar", on_click=register_clicked),
                    error_text,
                    ft.TextButton("Já tem uma conta? Faça login", on_click=go_to_login)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
