import sqlite3
import hashlib
import os
import logging

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
    conn = None
    try:
        logging.info(f"Conectando ao banco de dados: {DB_FILE}")
        conn = get_db_connection()
        cursor = conn.cursor()
        logging.info("Conexão com o banco de dados estabelecida.")

        # --- Criação das Tabelas ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
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

        # Tabela mestre de todos os exercícios disponíveis
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_exercises (
            master_exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            muscle_group TEXT NOT NULL
        )
        """)

        # Fichas de treino personalizadas para cada usuário
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_workouts (
            user_workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)

        # Exercícios específicos dentro da ficha de um usuário
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_exercises (
            user_exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_workout_id INTEGER NOT NULL,
            master_exercise_id INTEGER NOT NULL,
            series TEXT NOT NULL,
            FOREIGN KEY (user_workout_id) REFERENCES user_workouts(user_workout_id),
            FOREIGN KEY (master_exercise_id) REFERENCES master_exercises(master_exercise_id)
        )
        """)

        # --- Schema Migration ---
        cursor.execute("PRAGMA table_info(users)")
        columns = [row['name'] for row in cursor.fetchall()]
        if 'salt' not in columns:
            logging.info("Adicionando a coluna 'salt' à tabela 'users'.")
            cursor.execute("ALTER TABLE users ADD COLUMN salt TEXT NOT NULL DEFAULT ''")

        # --- Pré-popular a tabela de papéis (roles) ---
        try:
            roles_to_add = [('user',), ('admin',)]
            cursor.executemany("INSERT INTO roles (role_name) VALUES (?)", roles_to_add)
        except sqlite3.IntegrityError:
            # Papéis já existem, ignorar o erro
            pass

        # --- Popular a biblioteca de exercícios (master_exercises) ---
        master_exercise_list = [
            # Peito
            ('Supino Reto (Barra)', 'Peito'),
            ('Supino Reto (Halteres)', 'Peito'),
            ('Supino Inclinado (Barra)', 'Peito'),
            ('Supino Inclinado (Halteres)', 'Peito'),
            ('Supino Declinado (Barra)', 'Peito'),
            ('Crucifixo (Halteres)', 'Peito'),
            ('Crucifixo (Polia)', 'Peito'),
            ('Peck Deck (Máquina)', 'Peito'),
            ('Paralelas (Dips)', 'Peito'),
            ('Flexão', 'Peito'),
            # Costas
            ('Barra Fixa', 'Costas'),
            ('Puxada Alta (Frontal)', 'Costas'),
            ('Remada Curvada (Barra)', 'Costas'),
            ('Remada Cavalinho', 'Costas'),
            ('Remada Unilateral (Serrote)', 'Costas'),
            ('Pulldown (Braços Estendidos)', 'Costas'),
            ('Remada Sentada (Polia)', 'Costas'),
            # Pernas (Quadríceps)
            ('Agachamento Livre', 'Pernas'),
            ('Leg Press 45°', 'Pernas'),
            ('Afundo (Passada)', 'Pernas'),
            ('Agachamento Búlgaro', 'Pernas'),
            ('Cadeira Extensora', 'Pernas'),
            # Pernas (Posterior e Glúteos)
            ('Stiff (Romeno)', 'Pernas'),
            ('Cadeira Flexora', 'Pernas'),
            ('Mesa Flexora', 'Pernas'),
            ('Elevação Pélvica', 'Pernas'),
            # Panturrilhas
            ('Panturrilha em Pé (Gêmeos)', 'Pernas'),
            ('Panturrilha Sentado (Sóleo)', 'Pernas'),
            # Ombros
            ('Desenvolvimento (Halteres)', 'Ombros'),
            ('Desenvolvimento (Barra)', 'Ombros'),
            ('Elevação Lateral (Halteres)', 'Ombros'),
            ('Elevação Lateral (Polia)', 'Ombros'),
            ('Elevação Frontal (Halteres)', 'Ombros'),
            ('Crucifixo Invertido (Halteres)', 'Ombros'),
            ('Crucifixo Invertido (Peck Deck)', 'Ombros'),
            ('Remada Alta', 'Ombros'),
            # Bíceps
            ('Rosca Direta (Barra)', 'Bíceps'),
            ('Rosca Direta (Barra W)', 'Bíceps'),
            ('Rosca Alternada (Halteres)', 'Bíceps'),
            ('Rosca Scott', 'Bíceps'),
            ('Rosca Concentrada', 'Bíceps'),
            # Tríceps
            ('Tríceps Testa (Polia)', 'Tríceps'),
            ('Tríceps Testa (Barra W)', 'Tríceps'),
            ('Tríceps Corda (Polia)', 'Tríceps'),
            ('Mergulho no Banco', 'Tríceps'),
            ('Tríceps Francês (Halter)', 'Tríceps'),
            # Abdômen
            ('Abdominal Supra', 'Abdômen'),
            ('Abdominal Infra (na paralela)', 'Abdômen'),
            ('Prancha', 'Abdômen'),
            ('Elevação de Pernas', 'Abdômen'),
        ]
        try:
            cursor.executemany("INSERT INTO master_exercises (name, muscle_group) VALUES (?, ?)", master_exercise_list)
        except sqlite3.IntegrityError:
            # Dados já existem
            pass

        conn.commit()
        logging.info("Banco de dados inicializado com sucesso.")

    except sqlite3.Error as e:
        logging.error(f"Erro no banco de dados durante a inicialização: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logging.info("Conexão com o banco de dados fechada.")

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

    # Gerar salt e hashear a senha
    salt = os.urandom(16).hex()
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

    try:
        # Inserir o novo usuário
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, salt)
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

        # Criar treinos padrão para o novo usuário
        create_default_workouts_for_user(user_id, cursor)

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

    cursor.execute(
        "SELECT user_id, password_hash, salt FROM users WHERE username = ? OR email = ?",
        (identifier, identifier)
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return None

    # Hash da senha fornecida com o salt do usuário para comparação
    password_hash = hashlib.sha256((password + user['salt']).encode()).hexdigest()

    if user['password_hash'] == password_hash:
        conn.close()
        return user['user_id']

    conn.close()
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

def create_default_workouts_for_user(user_id, cursor):
    """Cria a cópia inicial dos treinos padrão para um novo usuário."""
    default_workouts = {
        "Treino A: Peito e Tríceps": [
            ("Supino Reto (Barra)", "4x8-10"),
            ("Supino Inclinado (Halteres)", "3x10-12"),
            ("Paralelas (Dips)", "3x10-12"),
            ("Crucifixo (Polia)", "3x12-15"),
            ("Tríceps Testa (Polia)", "4x10-12"),
            ("Tríceps Corda (Polia)", "3x12-15"),
        ],
        "Treino B: Quadríceps": [
            ("Agachamento Livre", "4x8-10"),
            ("Leg Press 45°", "3x10-12"),
            ("Afundo (Passada)", "3x10-12 (por perna)"),
            ("Cadeira Extensora", "3x15"),
            ("Panturrilha em Pé (Gêmeos)", "4x15-20"),
            ("Panturrilha Sentado (Sóleo)", "3x15-20"),
        ],
        "Treino C: Costas e Bíceps": [
            ("Barra Fixa", "4x10-12 (ou falha)"),
            ("Remada Curvada (Barra)", "4x8-10"),
            ("Remada Unilateral (Serrote)", "3x10-12"),
            ("Pulldown (Braços Estendidos)", "3x12-15"),
            ("Rosca Direta (Barra W)", "4x10-12"),
            ("Rosca Alternada (Halteres)", "3x10-12"),
        ],
        "Treino D: Ombro e Posterior": [
            ("Desenvolvimento (Halteres)", "4x8-10"),
            ("Elevação Lateral (Halteres)", "4x12-15"),
            ("Crucifixo Invertido (Halteres)", "3x12-15"),
            ("Elevação Frontal (Halteres)", "3x10-12"),
            ("Stiff (Romeno)", "4x10-12"),
            ("Cadeira Flexora", "3x12-15"),
        ]
    }

    for title, exercises in default_workouts.items():
        cursor.execute("INSERT INTO user_workouts (user_id, title) VALUES (?, ?)", (user_id, title))
        user_workout_id = cursor.lastrowid
        for ex_name, series in exercises:
            cursor.execute("SELECT master_exercise_id FROM master_exercises WHERE name = ?", (ex_name,))
            master_ex = cursor.fetchone()
            if master_ex:
                cursor.execute(
                    "INSERT INTO user_exercises (user_workout_id, master_exercise_id, series) VALUES (?, ?, ?)",
                    (user_workout_id, master_ex['master_exercise_id'], series)
                )

def get_user_workouts(user_id):
    """
    Busca todas as fichas de treino de um usuário.
    Se o usuário não tiver treinos, cria os treinos padrão para ele.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verifica se o usuário já tem treinos
    cursor.execute("SELECT COUNT(*) FROM user_workouts WHERE user_id = ?", (user_id,))
    workout_count = cursor.fetchone()[0]

    # Se não tiver, cria os treinos padrão
    if workout_count == 0:
        print(f"Nenhum treino encontrado para o user_id {user_id}. Criando treinos padrão...")
        create_default_workouts_for_user(user_id, cursor)
        conn.commit() # Efetiva a criação dos treinos

    # Busca os treinos (agora eles devem existir)
    cursor.execute("SELECT user_workout_id, title FROM user_workouts WHERE user_id = ?", (user_id,))
    workouts = cursor.fetchall()

    conn.close()
    return workouts

def get_user_workout_by_id(user_workout_id):
    """Busca os detalhes de uma ficha de treino específica, como o título."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM user_workouts WHERE user_workout_id = ?", (user_workout_id,))
    workout = cursor.fetchone()
    conn.close()
    return workout

def get_user_workout_details(user_workout_id):
    """Busca os detalhes (exercícios) de uma ficha de treino específica."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT ue.user_exercise_id, me.name, ue.series, ue.master_exercise_id
    FROM user_exercises ue
    JOIN master_exercises me ON ue.master_exercise_id = me.master_exercise_id
    WHERE ue.user_workout_id = ?
    ORDER BY ue.user_exercise_id
    """
    cursor.execute(query, (user_workout_id,))
    details = cursor.fetchall()
    conn.close()
    return details

def update_exercise_series(user_exercise_id, new_series):
    """Atualiza as séries de um exercício específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_exercises SET series = ? WHERE user_exercise_id = ?", (new_series, user_exercise_id))
    conn.commit()
    conn.close()

def replace_exercise_in_workout(user_exercise_id, new_master_exercise_id):
    """Substitui um exercício em uma ficha de treino."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_exercises SET master_exercise_id = ? WHERE user_exercise_id = ?", (new_master_exercise_id, user_exercise_id))
    conn.commit()
    conn.close()

def add_exercise_to_workout(user_workout_id, master_exercise_id, series="3x10"):
    """Adiciona um novo exercício a uma ficha de treino."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_exercises (user_workout_id, master_exercise_id, series) VALUES (?, ?, ?)",
        (user_workout_id, master_exercise_id, series)
    )
    conn.commit()
    conn.close()

def remove_exercise_from_workout(user_exercise_id):
    """Remove um exercício de uma ficha de treino."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_exercises WHERE user_exercise_id = ?", (user_exercise_id,))
    conn.commit()
    conn.close()

def get_all_master_exercises():
    """Busca todos os exercícios da biblioteca, agrupados por músculo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT master_exercise_id, name, muscle_group FROM master_exercises ORDER BY muscle_group, name")
    exercises = cursor.fetchall()
    conn.close()

    grouped_exercises = {}
    for ex in exercises:
        group = ex['muscle_group']
        if group not in grouped_exercises:
            grouped_exercises[group] = []
        grouped_exercises[group].append(ex)

    return grouped_exercises

def update_workout(user_workout_id, edited_data):
    """
    Atualiza uma ficha de treino inteira com base nos dados editados.
    Isso inclui o título do treino e a lista de exercícios (adicionar, remover, reordenar, atualizar séries).
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Atualizar o título do treino
        new_title = edited_data['details']['title']
        cursor.execute("UPDATE user_workouts SET title = ? WHERE user_workout_id = ?", (new_title, user_workout_id))

        # 2. Sincronizar os exercícios (delete all and re-insert)
        # Primeiro, deletamos todos os exercícios associados ao treino
        cursor.execute("DELETE FROM user_exercises WHERE user_workout_id = ?", (user_workout_id,))
        # Depois, inserimos todos os exercícios da lista editada na nova ordem
        for ex in edited_data['exercises']:
            # Garante que estamos pegando o ID correto, seja de um exercício existente ou novo
            master_id = ex.get('master_exercise_id')
            if not master_id:
                # Se for um exercício novo, o ID pode estar em 'id'
                master_id = ex.get('id')

            if master_id:
                 cursor.execute(
                    "INSERT INTO user_exercises (user_workout_id, master_exercise_id, series) VALUES (?, ?, ?)",
                    (user_workout_id, master_id, ex['series'])
                )

        conn.commit()

    except sqlite3.Error as e:
        print(f"Erro ao atualizar o treino: {e}")
        conn.rollback()
    finally:
        conn.close()
