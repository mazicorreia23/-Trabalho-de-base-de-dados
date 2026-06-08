from backend.database import conectar
from typing import Optional


def select_utilizador_por_credenciais(conta: str, senha_hash: str) -> Optional[tuple]:
    """Verifica se as credenciais são válidas e devolve o registo."""
    conn = conectar()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_utilizador FROM utilizador WHERE conta = ? AND palavra_passe = ?",
            (conta, senha_hash),
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Erro crítico durante o login: {e}")
        return None
    finally:
        conn.close()


def select_utilizador_por_conta(conta: str) -> Optional[tuple]:
    """Verifica se já existe um utilizador com esse nome (case-insensitive)."""
    conn = conectar()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_utilizador FROM utilizador WHERE LOWER(conta) = ?",
            (conta.lower(),),
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Erro ao verificar duplicação de conta: {e}")
        return None
    finally:
        conn.close()
