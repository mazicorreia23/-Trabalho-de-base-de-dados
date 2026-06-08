from backend.database import conectar


def select_count_tipos_consulta() -> int:
    """Devolve o número de linhas na tabela tipo_consulta."""
    conn = conectar()
    if not conn:
        return -1
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tipo_consulta")
        return cursor.fetchone()[0]
    except Exception as e:
        print(f"Erro ao contar tipos de consulta: {e}")
        return -1
    finally:
        conn.close()


def select_tipo_consulta_por_id(id_tipo: int):
    """Devolve descrição e custo de um tipo de consulta."""
    conn = conectar()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT descricao, custo FROM tipo_consulta WHERE id_tipo = ?", (id_tipo,)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Erro ao obter tipo de consulta: {e}")
        return None
    finally:
        conn.close()


def select_ids_tipos_consulta_existentes() -> set:
    """Devolve o conjunto de IDs já existentes na tabela tipo_consulta."""
    conn = conectar()
    if not conn:
        return set()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_tipo FROM tipo_consulta")
        return {row[0] for row in cursor.fetchall()}
    except Exception as e:
        print(f"Erro ao carregar IDs de tipos de consulta: {e}")
        return set()
    finally:
        conn.close()


def select_dividas_todos_utilizadores() -> list:
    """Devolve o relatório financeiro completo de todos os utilizadores (excl. admin)."""
    conn = conectar()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                u.conta,
                c.data_hora,
                t.descricao,
                t.custo,
                SUM(t.custo) OVER (PARTITION BY u.id_utilizador ORDER BY c.data_hora) AS custo_acumulado
            FROM utilizador u
            JOIN consulta c ON u.id_utilizador = c.id_utilizador
            JOIN tipo_consulta t ON c.id_tipo = t.id_tipo
            WHERE u.conta != 'admin'
            ORDER BY u.conta, c.data_hora
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao carregar relatório financeiro: {e}")
        return []
    finally:
        conn.close()


def select_receita_total() -> float:
    """Devolve a receita total gerada por todos os utilizadores (excl. admin)."""
    conn = conectar()
    if not conn:
        return 0.0
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT SUM(t.custo)
            FROM consulta c
            JOIN tipo_consulta t ON c.id_tipo = t.id_tipo
            JOIN utilizador u ON c.id_utilizador = u.id_utilizador
            WHERE u.conta != 'admin'
            """
        )
        resultado = cursor.fetchone()[0]
        return resultado if resultado else 0.0
    except Exception as e:
        print(f"Erro ao calcular receita total: {e}")
        return 0.0
    finally:
        conn.close()
