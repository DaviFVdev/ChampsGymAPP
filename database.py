import sqlite3
import hashlib
import os

DB_FILE = "champs_gym.db"

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Inicializa o banco de dados, criando as tabelas e os papéis (roles) iniciais
    se ainda não existirem.
    """
    if os.path.exists(DB_FILE):
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Criação das Tabelas ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        is_verified INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_roles (
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, role_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (role_id) REFERENCES roles(role_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_tokens (
        token_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token_hash TEXT NOT NULL UNIQUE,
        token_type TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
        route TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        series TEXT NOT NULL,
        FOREIGN KEY (workout_id) REFERENCES workouts(workout_id)
    )
    """)

    # --- Pré-popular a tabela de papéis (roles) ---
    try:
        roles_to_add = [('user',), ('admin',)]
        cursor.executemany("INSERT INTO roles (role_name) VALUES (?)", roles_to_add)
    except sqlite3.IntegrityError:
        # Papéis já existem, ignorar o erro
        pass

    # --- Pré-popular os dados de treino ---
    workout_data = {
        "/treino-a": {
            "title": "Treino A: Peito e Tríceps",
            "exercises": [
                ("Supino Reto (Barra)", "4x8-10"),
                ("Supino Inclinado (Halteres)", "3x10-12"),
                ("Paralelas (Dips) ou Supino Declinado", "3x10-12"),
                ("Crucifixo (Polia ou Halteres)", "3x12-15"),
                ("Tríceps Testa (Polia ou Barra W)", "4x10-12"),
                ("Tríceps Corda (Polia)", "3x12-15"),
            ]
        },
        "/treino-b": {
            "title": "Treino B: Quadríceps",
            "exercises": [
                ("Agachamento Livre", "4x8-10"),
                ("Leg Press 45°", "3x10-12"),
                ("Afundo (Passada) ou Búlgaro", "3x10-12 (por perna)"),
                ("Cadeira Extensora", "3x15"),
                ("Panturrilha em Pé (Gêmeos)", "4x15-20"),
                ("Panturrilha Sentado (Sóleo)", "3x15-20"),
            ]
        },
        "/treino-c": {
            "title": "Treino C: Costas e Bíceps",
            "exercises": [
                ("Barra Fixa ou Puxada Alta (Frontal)", "4x10-12 (ou falha)"),
                ("Remada Curvada (Barra) ou Cavalinho", "4x8-10"),
                ("Remada Unilateral (Serrote)", "3x10-12"),
                ("Pulldown (Braços Estendidos)", "3x12-15"),
                ("Rosca Direta (Barra W)", "4x10-12"),
                ("Rosca Alternada (Halteres)", "3x10-12"),
            ]
        },
        "/treino-d": {
            "title": "Treino D: Ombro e Posterior",
            "exercises": [
                ("Desenvolvimento (Halteres ou Barra)", "4x8-10"),
                ("Elevação Lateral (Halteres ou Polia)", "4x12-15"),
                ("Crucifixo Invertido (Halteres ou Peck Deck)", "3x12-15"),
                ("Elevação Frontal (Halteres)", "3x10-12"),
                ("Stiff (Romeno) (Barra ou Halteres)", "4x10-12"),
                ("Cadeira Flexora (Deitado ou Sentado)", "3x12-15"),
            ]
        }
    }

    try:
        for route, data in workout_data.items():
            cursor.execute("INSERT INTO workouts (route, title) VALUES (?, ?)", (route, data["title"]))
            workout_id = cursor.lastrowid
            for exercise in data["exercises"]:
                cursor.execute(
                    "INSERT INTO exercises (workout_id, name, series) VALUES (?, ?, ?)",
                    (workout_id, exercise[0], exercise[1])
                )
    except sqlite3.IntegrityError:
        # Dados já existem
        pass

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso.")

def add_user(username, email, password):
    """
    Adiciona um novo usuário ao banco de dados com o papel 'user'.

    Retorna True se o usuário for criado com sucesso, False caso contrário
    (ex: usuário ou e-mail já existente).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se username ou email já existem
    cursor.execute("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        conn.close()
        return False  # Usuário ou e-mail já cadastrado

    # Hash da senha
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    try:
        # Inserir o novo usuário
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        user_id = cursor.lastrowid

        # Obter o role_id para 'user'
        cursor.execute("SELECT role_id FROM roles WHERE role_name = 'user'")
        role_result = cursor.fetchone()
        if not role_result:
            # Isso não deve acontecer se init_db foi chamado, mas é uma segurança
            conn.rollback()
            conn.close()
            raise Exception("O papel 'user' não foi encontrado no banco de dados.")

        user_role_id = role_result['role_id']

        # Associar o usuário ao papel 'user'
        cursor.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)",
            (user_id, user_role_id)
        )

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Para testar a criação do banco de dados ao executar este arquivo diretamente
if __name__ == '__main__':
    init_db()

def verify_user(identifier, password):
    """
    Verifica as credenciais do usuário.

    Retorna o user_id se a autenticação for bem-sucedida, None caso contrário.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Hash da senha fornecida para comparação
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute(
        "SELECT user_id, password_hash FROM users WHERE username = ? OR email = ?",
        (identifier, identifier)
    )
    user = cursor.fetchone()
    conn.close()

    if user and user['password_hash'] == password_hash:
        return user['user_id']

    return None

def get_user_by_id(user_id):
    """
    Busca um usuário pelo seu ID.

    Retorna um dicionário com os dados do usuário ou None se não encontrado.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_workout_by_route(route):
    """
    Busca uma ficha de treino e seus exercícios pelo campo 'route'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Busca o workout principal
    cursor.execute("SELECT * FROM workouts WHERE route = ?", (route,))
    workout = cursor.fetchone()

    if not workout:
        conn.close()
        return None

    # Busca os exercícios associados
    cursor.execute("SELECT name, series FROM exercises WHERE workout_id = ?", (workout['workout_id'],))
    exercises = cursor.fetchall()

    conn.close()

    # Monta a estrutura de dados para a tela
    return {
        "title": workout['title'],
        "exercises": [{"name": ex['name'], "series": ex['series']} for ex in exercises]
    }
