from backend.database import conectar


def update_placar_jogo(id_jogo, g_casa: int, g_fora: int) -> bool:
    """Atualiza o placar de um jogo existente."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE jogo SET golos_casa = ?, golos_fora = ? WHERE id_jogo = ?",
            (g_casa, g_fora, id_jogo),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar placar: {e}")
        return False
    finally:
        conn.close()


def update_password_utilizador(id_utilizador, senha_hash: str) -> bool:
    """Atualiza a palavra-passe de um utilizador."""
    conn = conectar()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE utilizador SET palavra_passe = ? WHERE id_utilizador = ?",
            (senha_hash, id_utilizador),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao editar utilizador: {e}")
        return False
    finally:
        conn.close()
