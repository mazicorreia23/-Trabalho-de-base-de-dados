from backend.database import conectar


def select_golos_por_jogador(nome_jogador: str) -> list:
    """Quantos golos o jogador X marcou no campeonato."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.nome, e.nome AS equipa, COUNT(g.id_golo) AS total_golos
            FROM jogador j
            JOIN equipa e ON j.id_equipa = e.id_equipa
            LEFT JOIN golo g ON j.id_jogador = g.id_jogador
            WHERE LOWER(j.nome) LIKE LOWER(?)
            GROUP BY j.id_jogador
            ORDER BY total_golos DESC
            """,
            (f"%{nome_jogador}%",),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao contar golos do jogador: {e}")
        return []
    finally:
        conn.close()


def select_artilharia_liga() -> list:
    """Artilharia da liga - jogador(es) com mais golos."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.nome, e.nome AS equipa, COUNT(g.id_golo) AS total_golos
            FROM jogador j
            JOIN equipa e ON j.id_equipa = e.id_equipa
            JOIN golo g ON j.id_jogador = g.id_jogador
            GROUP BY j.id_jogador
            HAVING total_golos = (
                SELECT MAX(cnt) FROM (
                    SELECT COUNT(id_golo) AS cnt
                    FROM golo
                    GROUP BY id_jogador
                )
            )
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao calcular artilharia: {e}")
        return []
    finally:
        conn.close()


def select_total_golos_por_equipa() -> list:
    """Total de golos marcados por cada equipa."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e.nome, COUNT(g.id_golo) AS total_golos
            FROM equipa e
            LEFT JOIN jogador j ON e.id_equipa = j.id_equipa
            LEFT JOIN golo g ON j.id_jogador = g.id_jogador
            GROUP BY e.id_equipa
            ORDER BY total_golos DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao calcular golos por equipa: {e}")
        return []
    finally:
        conn.close()


def select_partidas_por_equipa() -> list:
    """Quantidade de partidas realizadas por cada equipa."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e.nome,
                   COUNT(DISTINCT j.id_jogo) AS total_partidas
            FROM equipa e
            LEFT JOIN jogo j ON e.id_equipa = j.id_equipa_casa OR e.id_equipa = j.id_equipa_fora
            GROUP BY e.id_equipa
            ORDER BY total_partidas DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao contar partidas por equipa: {e}")
        return []
    finally:
        conn.close()


def select_custo_total_por_utilizador() -> list:
    """Custo total das consultas realizadas por cada utilizador."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.conta, COALESCE(SUM(t.custo), 0.0) AS total_gasto
            FROM utilizador u
            LEFT JOIN consulta c ON u.id_utilizador = c.id_utilizador
            LEFT JOIN tipo_consulta t ON c.id_tipo = t.id_tipo
            WHERE u.conta != 'admin'
            GROUP BY u.id_utilizador
            ORDER BY total_gasto DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao calcular custo por utilizador: {e}")
        return []
    finally:
        conn.close()
