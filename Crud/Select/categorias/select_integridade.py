from backend.database import conectar


def select_jogadores_sem_equipa() -> list:
    """Devolve jogadores órfãos (sem equipa)."""
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


def select_jogos_golos_negativos() -> list:
    """Testes de integridade: jogos com golos negativos."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_jogo FROM jogo WHERE golos_casa < 0 OR golos_fora < 0")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro no teste de integridade: {e}")
        return []
    finally:
        conn.close()


def select_jogos_equipa_contra_si() -> list:
    """Testes de integridade: jogos onde uma equipa joga contra si mesma."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_jogo FROM jogo WHERE id_equipa_casa = id_equipa_fora")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro no teste de integridade: {e}")
        return []
    finally:
        conn.close()


def select_golos_minutos_invalidos() -> list:
    """Testes de integridade: golos com minutos fora do intervalo válido."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_golo FROM golo WHERE minuto < 1 OR minuto > 130")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro no teste de integridade: {e}")
        return []
    finally:
        conn.close()
