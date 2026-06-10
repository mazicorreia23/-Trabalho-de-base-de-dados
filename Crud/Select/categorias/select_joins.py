from backend.database import conectar


def select_jogos_com_placar() -> list:
    """Lista todas as partidas com o placar."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ec.nome, ef.nome, j.golos_casa, j.golos_fora
            FROM jogo j
            JOIN equipa ec ON j.id_equipa_casa = ec.id_equipa
            JOIN equipa ef ON j.id_equipa_fora = ef.id_equipa
            ORDER BY j.data
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar placares: {e}")
        return []
    finally:
        conn.close()


def select_jogadores_que_marcaram_em_jogo(id_jogo: int) -> list:
    """Lista os jogadores que marcaram golos numa partida específica, com nome e equipa."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.nome, e.nome AS equipa, g.minuto
            FROM golo g
            JOIN jogador j ON g.id_jogador = j.id_jogador
            JOIN equipa e ON j.id_equipa = e.id_equipa
            WHERE g.id_jogo = ?
            ORDER BY g.minuto
            """,
            (id_jogo,),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter marcadores do jogo: {e}")
        return []
    finally:
        conn.close()


def select_historico_consultas(id_utilizador: int) -> list:
    """Devolve o histórico de consultas com custo acumulado do utilizador."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.data_hora, t.descricao, t.custo,
                   SUM(t.custo) OVER (ORDER BY c.data_hora) AS acumulado
            FROM consulta c
            JOIN tipo_consulta t ON c.id_tipo = t.id_tipo
            WHERE c.id_utilizador = ?
            ORDER BY c.data_hora
            """,
            (id_utilizador,),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao carregar histórico: {e}")
        return []
    finally:
        conn.close()
