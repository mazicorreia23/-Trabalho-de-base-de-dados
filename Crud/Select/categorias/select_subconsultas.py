from backend.database import conectar


def select_jogadores_acima_media() -> list:
    """Jogadores com mais golos do que a média da liga."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.nome, e.nome, COUNT(g.id_golo) AS total
            FROM jogador j
            JOIN equipa e ON j.id_equipa = e.id_equipa
            JOIN golo g ON j.id_jogador = g.id_jogador
            GROUP BY j.id_jogador
            HAVING total > (
                SELECT CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT id_jogador) FROM golo
            )
            ORDER BY total DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao consultar média de golos: {e}")
        return []
    finally:
        conn.close()


def select_equipas_que_nunca_ganharam() -> list:
    """Times que nunca ganharam nenhuma partida (subconsulta)."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nome FROM equipa WHERE id_equipa NOT IN (
                SELECT id_equipa_casa FROM jogo WHERE golos_casa > golos_fora
                UNION
                SELECT id_equipa_fora FROM jogo WHERE golos_fora > golos_casa
            )
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao calcular equipas sem vitórias: {e}")
        return []
    finally:
        conn.close()
