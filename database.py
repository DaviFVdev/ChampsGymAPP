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

    # --- Pré-popular a tabela de papéis (roles) ---
    try:
        cursor.execute("INSERT INTO roles (role_name) VALUES (?), (?)", ('user', 'admin'))
    except sqlite3.IntegrityError:
        # Papéis já existem, ignorar o erro
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
