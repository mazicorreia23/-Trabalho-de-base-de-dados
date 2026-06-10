from backend.auth.auth import encriptar_senha
from Crud.Insert.insert_queries import insert_admin


def recriar_admin():
    senha_hash = encriptar_senha('123456')
    if insert_admin(senha_hash):
        print("Administrador recriado com sucesso!")


if __name__ == "__main__":
    recriar_admin()
