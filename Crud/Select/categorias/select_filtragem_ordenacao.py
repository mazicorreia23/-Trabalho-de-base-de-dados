from backend.database import conectar


def select_jogadores_mais_5_golos() -> list:
    """Jogadores com mais de 5 golos, por ordem decrescente."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.nome, e.nome, COUNT(g.id_golo) AS total
            FROM jogador j
            JOIN golo g ON j.id_jogador = g.id_jogador
            JOIN equipa e ON j.id_equipa = e.id_equipa
            GROUP BY j.id_jogador
            HAVING total > 5
            ORDER BY total DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao consultar artilheiros: {e}")
        return []
    finally:
        conn.close()


def select_jogadores_curinga(nome_pesquisa: str) -> list:
    """Pesquisa jogadores pelo nome usando LIKE."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.nome, j.posicao, e.nome
            FROM jogador j
            JOIN equipa e ON j.id_equipa = e.id_equipa
            WHERE j.nome LIKE ?
            """,
            (f"%{nome_pesquisa}%",),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro na pesquisa curinga: {e}")
        return []
    finally:
        conn.close()


def select_partidas_por_local(local: str) -> list:
    """Lista partidas realizadas num determinado local."""
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
            WHERE LOWER(j.local) LIKE LOWER(?)
            ORDER BY j.data DESC
            """,
            (f"%{local}%",),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao filtrar partidas por local: {e}")
        return []
    finally:
        conn.close()


def select_utilizadores_por_periodo(data_inicio: str, data_fim: str) -> list:
    """Utilizadores que realizaram consultas num período específico."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT u.conta, COUNT(c.id_consulta) AS total_consultas
            FROM utilizador u
            JOIN consulta c ON u.id_utilizador = c.id_utilizador
            WHERE c.data_hora BETWEEN ? AND ?
              AND u.conta != 'admin'
            GROUP BY u.id_utilizador
            ORDER BY total_consultas DESC
            """,
            (data_inicio, data_fim),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao filtrar utilizadores por período: {e}")
        return []
    finally:
        conn.close()
