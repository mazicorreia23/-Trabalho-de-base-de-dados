from backend.database import conectar


def delete_golos_por_jogo(id_jogo) -> bool:
    """Remove todos os golos associados a um jogo."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM golo WHERE id_jogo = ?", (id_jogo,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao remover golos do jogo: {e}")
        return False
    finally:
        conn.close()


def delete_jogo(id_jogo) -> bool:
    """Remove um jogo (deve ser chamado após delete_golos_por_jogo)."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jogo WHERE id_jogo = ?", (id_jogo,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao remover jogo: {e}")
        return False
    finally:
        conn.close()


def delete_consultas_por_utilizador(id_utilizador) -> int:
    """Remove todo o histórico de consultas de um utilizador. Devolve nº de linhas apagadas."""
    conn = conectar()
    if not conn:
        return 0
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM consulta WHERE id_utilizador = ?", (id_utilizador,))
        linhas = cursor.rowcount
        conn.commit()
        return linhas
    except Exception as e:
        print(f"Erro ao limpar dívida: {e}")
        return 0
    finally:
        conn.close()


def delete_utilizador(id_utilizador) -> bool:
    """Remove um utilizador (deve ser chamado após delete_consultas_por_utilizador)."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM utilizador WHERE id_utilizador = ?", (id_utilizador,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao remover utilizador: {e}")
        return False
    finally:
        conn.close()
