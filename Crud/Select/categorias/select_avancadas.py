from backend.database import conectar


def select_top5_artilheiros() -> list:
    """Top 5 artilheiros usando RANK() OVER()."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM (
                SELECT j.nome, e.nome AS equipa, COUNT(g.id_golo) AS total,
                       RANK() OVER (ORDER BY COUNT(g.id_golo) DESC) AS ranking
                FROM jogador j
                JOIN golo g ON j.id_jogador = g.id_jogador
                JOIN equipa e ON j.id_equipa = e.id_equipa
                GROUP BY j.id_jogador
            ) WHERE ranking <= 5
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao calcular top artilheiros: {e}")
        return []
    finally:
        conn.close()


def select_jogos_com_vencedor() -> list:
    """Jogos em que houve um vencedor (sem empate)."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                j.data,
                e1.nome AS casa,
                e2.nome AS fora,
                j.golos_casa,
                j.golos_fora,
                CASE
                    WHEN j.golos_casa > j.golos_fora THEN e1.nome
                    ELSE e2.nome
                END AS vencedor
            FROM jogo j
            JOIN equipa e1 ON j.id_equipa_casa = e1.id_equipa
            JOIN equipa e2 ON j.id_equipa_fora = e2.id_equipa
            WHERE j.golos_casa != j.golos_fora
            ORDER BY j.data DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar jogos com vencedor: {e}")
        return []
    finally:
        conn.close()


def select_equipas_invictas() -> list:
    """Equipas que nunca perderam (NOT IN + UNION)."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nome FROM equipa WHERE id_equipa NOT IN (
                SELECT id_equipa_casa FROM jogo WHERE golos_casa < golos_fora
                UNION
                SELECT id_equipa_fora FROM jogo WHERE golos_fora < golos_casa
            )
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao calcular equipas invictas: {e}")
        return []
    finally:
        conn.close()


def select_jogos_acima_media_golos() -> list:
    """Partidas cuja soma de golos superou a média geral."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e1.nome, e2.nome, j.golos_casa, j.golos_fora,
                   (j.golos_casa + j.golos_fora) AS total_jogo
            FROM jogo j
            JOIN equipa e1 ON j.id_equipa_casa = e1.id_equipa
            JOIN equipa e2 ON j.id_equipa_fora = e2.id_equipa
            WHERE total_jogo > (
                SELECT CAST(SUM(golos_casa + golos_fora) AS FLOAT) / COUNT(id_jogo)
                FROM jogo WHERE golos_casa IS NOT NULL
            )
            ORDER BY total_jogo DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao calcular média de golos por jogo: {e}")
        return []
    finally:
        conn.close()
