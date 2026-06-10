import os
from datetime import datetime
from backend.auth.auth import encriptar_senha
from Crud.Select.categorias.select_basicas import (
    select_todos_utilizadores,
    select_utilizador_por_id,
)
from Crud.Select.categorias.select_auth import select_utilizador_por_conta
from Crud.Insert.insert_queries import insert_utilizador
from Crud.Update.update_queries import update_password_utilizador
from Crud.Delete.delete_queries import delete_consultas_por_utilizador, delete_utilizador

PASTA_LOGS = "logs"
FICHEIRO_LOG_USERS = "auditoria_utilizadores.log"


def registar_log(nome_ficheiro: str, acao: str, detalhes: str) -> None:
    os.makedirs(PASTA_LOGS, exist_ok=True)
    caminho_completo = os.path.join(PASTA_LOGS, nome_ficheiro)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensagem = f"[{data_hora}] AÇÃO: {acao} | DETALHES: {detalhes}\n"
    try:
        with open(caminho_completo, "a", encoding="utf-8") as ficheiro:
            ficheiro.write(mensagem)
    except Exception as e:
        print(f"[Aviso] Não foi possível escrever no log: {e}")


def ver_logs_no_terminal() -> None:
    arquivo_log = os.path.join(PASTA_LOGS, FICHEIRO_LOG_USERS)
    print("\n" + "=" * 70)
    print("HISTÓRICO DE AUDITORIA (UTILIZADORES)")
    print("=" * 70)
    try:
        if os.path.exists(arquivo_log):
            with open(arquivo_log, "r", encoding="utf-8") as ficheiro:
                conteudo = ficheiro.read()
                print(conteudo.strip() if conteudo.strip() else "O ficheiro de log está vazio.")
        else:
            print("Ainda não existem registos de log de utilizadores.")
    except Exception as e:
        print(f"Erro ao ler os logs: {e}")
    finally:
        print("=" * 70)


def listar_utilizadores() -> bool:
    utilizadores = select_todos_utilizadores()
    print("\n--- LISTA DE UTILIZADORES ---")
    if not utilizadores:
        print("Não existem utilizadores registados.")
        return False
    for id_user, conta in utilizadores:
        print(f"ID: {id_user:<3} | Conta: {conta}")
    print("-" * 29)
    return True


def adicionar_utilizador() -> None:
    print("\n-- ADICIONAR UTILIZADOR --")
    conta = input("Nova conta: ").strip()
    if not conta:
        print("Erro: O nome da conta não pode estar vazio.")
        return
    if conta.lower() == 'admin':
        print("Erro: Não podes duplicar a conta de Administrador.")
        return
    senha = input("Palavra-passe: ").strip()
    if not senha:
        print("Erro: A palavra-passe não pode estar vazia.")
        return

    if select_utilizador_por_conta(conta):
        print("Erro: Esta conta já existe no sistema.")
        return

    senha_hash = encriptar_senha(senha)
    if insert_utilizador(conta, senha_hash):
        print(f"Sucesso: Utilizador '{conta}' criado!")
        registar_log(FICHEIRO_LOG_USERS, "INSERÇÃO", f"Conta '{conta}' criada.")


def editar_utilizador() -> None:
    if not listar_utilizadores():
        return
    id_editar = input("\nDigita o ID do utilizador a editar (ou 0 para cancelar): ").strip()
    if id_editar == '0' or not id_editar:
        return

    resultado = select_utilizador_por_id(id_editar)
    if not resultado:
        print("Erro: ID inválido ou tentativa de alterar o Administrador.")
        return

    nome_conta = resultado[0]
    nova_senha = input(f"Digita a nova palavra-passe para '{nome_conta}': ").strip()
    if not nova_senha:
        print("Erro: A palavra-passe não pode estar vazia.")
        return

    senha_hash = encriptar_senha(nova_senha)
    if update_password_utilizador(id_editar, senha_hash):
        print(f"Sucesso: Palavra-passe de '{nome_conta}' atualizada!")
        registar_log(FICHEIRO_LOG_USERS, "ALTERAÇÃO", f"Palavra-passe da conta '{nome_conta}' (ID: {id_editar}) alterada.")


def limpar_divida_utilizador() -> None:
    if not listar_utilizadores():
        return
    id_limpar = input("\nDigita o ID do utilizador para limpar a dívida (ou 0 para cancelar): ").strip()
    if id_limpar == '0' or not id_limpar:
        return

    resultado = select_utilizador_por_id(id_limpar)
    if not resultado:
        print("Erro: ID inválido.")
        return

    nome_conta = resultado[0]
    linhas_apagadas = delete_consultas_por_utilizador(id_limpar)
    if linhas_apagadas > 0:
        print(f"Sucesso: Dívida de '{nome_conta}' liquidada! ({linhas_apagadas} registos removidos)")
        registar_log(FICHEIRO_LOG_USERS, "PAGAMENTO", f"Dívida da conta '{nome_conta}' (ID: {id_limpar}) liquidada.")
    else:
        print(f"O utilizador '{nome_conta}' não tinha dívidas pendentes.")


def remover_utilizador() -> None:
    if not listar_utilizadores():
        return
    id_remover = input("\nDigita o ID do utilizador a remover (ou 0 para cancelar): ").strip()
    if id_remover == '0' or not id_remover:
        return

    resultado = select_utilizador_por_id(id_remover)
    if not resultado:
        print("Erro: ID inválido ou tentativa de apagar o Administrador.")
        return

    nome_conta = resultado[0]
    delete_consultas_por_utilizador(id_remover)
    if delete_utilizador(id_remover):
        print(f"Sucesso: Utilizador '{nome_conta}' e o seu histórico foram removidos!")
        registar_log(FICHEIRO_LOG_USERS, "REMOÇÃO", f"Conta '{nome_conta}' (ID: {id_remover}) apagada.")


def menu_gerir_utilizadores() -> None:
    while True:
        print("\n=== GERIR UTILIZADORES ===")
        print("1. Listar Utilizadores")
        print("2. Adicionar Utilizador")
        print("3. Editar Utilizador (Palavra-passe)")
        print("4. Remover Utilizador")
        print("5. Registar Pagamento (Limpar Dívida)")
        print("6. Visualizar LOGs no Terminal")
        print("7. Voltar ao Painel Geral")
        escolha = input("Opção: ").strip()
        if escolha == '1':   listar_utilizadores()
        elif escolha == '2': adicionar_utilizador()
        elif escolha == '3': editar_utilizador()
        elif escolha == '4': remover_utilizador()
        elif escolha == '5': limpar_divida_utilizador()
        elif escolha == '6': ver_logs_no_terminal()
        elif escolha == '7': break
        else:                print("Opção inválida!")
