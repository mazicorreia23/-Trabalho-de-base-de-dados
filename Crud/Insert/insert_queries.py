from backend.database import conectar
from datetime import datetime


# ---------------------------------------------------------------------------
# UTILIZADORES
# ---------------------------------------------------------------------------

def insert_utilizador(conta: str, senha_hash: str) -> bool:
    """Insere um novo utilizador na base de dados."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO utilizador (conta, palavra_passe) VALUES (?, ?)",
            (conta, senha_hash),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao inserir utilizador: {e}")
        return False
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# TIPOS DE CONSULTA (inicialização)
# ---------------------------------------------------------------------------

def insert_tipos_consulta_default(precos: list) -> bool:
    """Insere os tipos de consulta e preços padrão."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO tipo_consulta (descricao, custo) VALUES (?, ?)", precos
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao inserir tipos de consulta: {e}")
        return False
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CONSULTAS (faturação)
# ---------------------------------------------------------------------------

def insert_consulta(id_utilizador: int, id_tipo: int) -> bool:
    """Regista uma consulta paga no histórico."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO consulta (id_utilizador, id_tipo, data_hora) VALUES (?, ?, ?)",
            (id_utilizador, id_tipo, data_hora),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao registar consulta: {e}")
        return False
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# EQUIPAS
# ---------------------------------------------------------------------------

def insert_equipa(nome: str, cidade: str | None) -> bool:
    """Insere uma nova equipa."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO equipa (nome, cidade) VALUES (?, ?)", (nome, cidade)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar equipa: {e}")
        return False
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# JOGADORES
# ---------------------------------------------------------------------------

def insert_jogador(nome: str, posicao: str, id_equipa: int) -> bool:
    """Insere um novo jogador."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO jogador (nome, posicao, id_equipa) VALUES (?, ?, ?)",
            (nome, posicao, id_equipa),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar jogador: {e}")
        return False
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# JOGOS
# ---------------------------------------------------------------------------

def insert_jogo(data: str, local: str, id_casa, id_fora, g_casa, g_fora) -> bool:
    """Insere um novo jogo."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO jogo (data, local, id_equipa_casa, id_equipa_fora, golos_casa, golos_fora)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (data, local, id_casa, id_fora, g_casa, g_fora),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao inserir jogo: {e}")
        return False
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# GOLOS
# ---------------------------------------------------------------------------

def insert_golo(id_jogo: int, id_jogador: int, minuto: int) -> bool:
    """Regista um golo."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO golo (id_jogo, id_jogador, minuto) VALUES (?, ?, ?)",
            (id_jogo, id_jogador, minuto),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao registar golo (verifica se os IDs de jogo e jogador existem): {e}")
        return False
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# ADMIN (recuperação)
# ---------------------------------------------------------------------------

def insert_admin(senha_hash: str) -> bool:
    """Insere directamente a conta admin (uso em recuperar_admin)."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO utilizador (conta, palavra_passe) VALUES (?, ?)",
            ("admin", senha_hash),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False
    finally:
        conn.close()


def insert_tipo_consulta_individual(id_tipo: int, descricao: str, custo: float) -> bool:
    """Insere um tipo de consulta com ID explícito (para migrações)."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tipo_consulta (id_tipo, descricao, custo) VALUES (?, ?, ?)",
            (id_tipo, descricao, custo),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao inserir tipo {id_tipo}: {e}")
        return False
    finally:
        conn.close()
