from backend.database import conectar


# ---------------------------------------------------------------------------
# EQUIPAS
# ---------------------------------------------------------------------------

def select_todas_equipas() -> list:
    """Lista todas as equipas ordenadas pelo nome."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_equipa, nome, cidade FROM equipa ORDER BY nome")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar equipas: {e}")
        return []
    finally:
        conn.close()


def select_equipas_nome_cidade() -> list:
    """Devolve nome e cidade de todas as equipas (para o menu utilizador)."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nome, cidade FROM equipa")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar equipas: {e}")
        return []
    finally:
        conn.close()


def select_equipa_por_id(id_equipa) -> tuple | None:
    """Devolve o nome de uma equipa pelo seu ID."""
    conn = conectar()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM equipa WHERE id_equipa = ?", (id_equipa,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Erro ao procurar equipa: {e}")
        return None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# JOGADORES
# ---------------------------------------------------------------------------

def select_todos_jogadores() -> list:
    """Lista todos os jogadores com o nome da equipa, ordenados."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.id_jogador, j.nome, j.posicao, e.nome
            FROM jogador j
            JOIN equipa e ON j.id_equipa = e.id_equipa
            ORDER BY e.nome, j.nome
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar jogadores: {e}")
        return []
    finally:
        conn.close()


def select_jogadores_por_equipa(id_equipa) -> list:
    """Lista os jogadores de uma equipa específica."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nome, posicao, idade FROM jogador WHERE id_equipa = ?",
            (id_equipa,),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar jogadores da equipa: {e}")
        return []
    finally:
        conn.close()


def select_jogadores_por_equipa_nome(nome_equipa: str) -> list:
    """Lista os jogadores de uma equipa específica pelo nome da equipa."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.nome, j.posicao, j.idade
            FROM jogador j
            JOIN equipa e ON j.id_equipa = e.id_equipa
            WHERE LOWER(e.nome) LIKE LOWER(?)
            ORDER BY j.nome
            """,
            (f"%{nome_equipa}%",),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar jogadores da equipa: {e}")
        return []
    finally:
        conn.close()


def select_jogadores_sem_equipa() -> list:
    """Devolve jogadores órfãos (sem equipa) — para testes de integridade."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_jogador FROM jogador WHERE id_equipa IS NULL")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro no teste de integridade de jogadores: {e}")
        return []
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# PARTIDAS
# ---------------------------------------------------------------------------

def select_todos_jogos() -> list:
    """Lista todos os jogos com os nomes das equipas, por data descendente."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.id_jogo, j.data, e1.nome, e2.nome, j.golos_casa, j.golos_fora
            FROM jogo j
            JOIN equipa e1 ON j.id_equipa_casa = e1.id_equipa
            JOIN equipa e2 ON j.id_equipa_fora = e2.id_equipa
            ORDER BY j.data DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar jogos: {e}")
        return []
    finally:
        conn.close()


def select_jogo_por_id(id_jogo) -> tuple | None:
    """Verifica se um jogo existe pelo seu ID."""
    conn = conectar()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_jogo FROM jogo WHERE id_jogo = ?", (id_jogo,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Erro ao verificar jogo: {e}")
        return None
    finally:
        conn.close()


def select_todas_partidas_com_local() -> list:
    """Exibe todas as partidas com data, local e times envolvidos."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.data, j.local, e1.nome, e2.nome, j.golos_casa, j.golos_fora
            FROM jogo j
            JOIN equipa e1 ON j.id_equipa_casa = e1.id_equipa
            JOIN equipa e2 ON j.id_equipa_fora = e2.id_equipa
            ORDER BY j.data DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar partidas: {e}")
        return []
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# UTILIZADORES
# ---------------------------------------------------------------------------

def select_id_utilizador(conta: str):
    """Devolve o ID do utilizador com base no nome da conta."""
    conn = conectar()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_utilizador FROM utilizador WHERE conta = ?", (conta,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"Erro ao obter ID do utilizador: {e}")
        return None
    finally:
        conn.close()


def select_utilizador_por_id(id_utilizador: str):
    """Devolve a conta de um utilizador (não-admin) pelo seu ID."""
    conn = conectar()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT conta FROM utilizador WHERE id_utilizador = ? AND conta != 'admin'",
            (id_utilizador,),
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Erro ao procurar utilizador por ID: {e}")
        return None
    finally:
        conn.close()


def select_todos_utilizadores() -> list:
    """Lista todos os utilizadores excepto o admin, por ordem de ID."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_utilizador, conta FROM utilizador WHERE conta != 'admin' ORDER BY id_utilizador"
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar utilizadores: {e}")
        return []
    finally:
        conn.close()
