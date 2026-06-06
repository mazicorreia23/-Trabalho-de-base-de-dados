from backend.database import conectar
from backend.auth import encriptar_senha

def recriar_admin():
    conn = conectar()
    if not conn:
        print("Erro na conexão.")
        return

    try:
        cursor = conn.cursor()
        # Encriptamos a password 'admin' (ou a que quiseres)
        senha_hash = encriptar_senha('admin') 
        
        # Inserção direta ignorando a lógica de validação do auth.py
        cursor.execute("INSERT INTO utilizador (conta, palavra_passe) VALUES (?, ?)", ('admin', senha_hash))
        conn.commit()
        print("Administrador recriado com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    recriar_admin()