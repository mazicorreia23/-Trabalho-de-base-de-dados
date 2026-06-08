import hashlib
from typing import Optional

from Crud.Select.categorias.select_auth import select_utilizador_por_credenciais, select_utilizador_por_conta
from Crud.Insert.insert_queries import insert_utilizador

ADMIN_USERNAME = 'admin'
ROLE_ADMIN = 'admin'
ROLE_USER = 'user'


def encriptar_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def registar_utilizador(conta: str, senha: str) -> bool:
    conta_limpa = conta.strip()

    if conta_limpa.lower() == ADMIN_USERNAME:
        print("Erro de Segurança: Não podes registar uma conta com o nome de Administrador!")
        return False

    senha_hash = encriptar_senha(senha)

    if select_utilizador_por_conta(conta_limpa):
        print("Erro: Esta conta já existe! Escolhe outro nome de utilizador.")
        return False

    if insert_utilizador(conta_limpa, senha_hash):
        print(f"Sucesso: Utilizador '{conta_limpa}' registado com sucesso!")
        return True
    return False


def fazer_login(conta: str, senha: str) -> Optional[str]:
    senha_hash = encriptar_senha(senha)
    resultado = select_utilizador_por_credenciais(conta, senha_hash)

    if not resultado:
        print("Erro: Conta ou palavra-passe incorretos.")
        return None

    print(f"\nBem-vindo, {conta}!")
    return ROLE_ADMIN if conta.lower() == ADMIN_USERNAME else ROLE_USER
