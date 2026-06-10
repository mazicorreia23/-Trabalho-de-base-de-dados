from typing import Optional
from backend.admin.gerir_utilizadores import registar_log
from Crud.Select.categorias.select_basicas import select_todos_jogos, select_jogo_por_id, select_todas_equipas
from Crud.Insert.insert_queries import insert_jogo
from Crud.Update.update_queries import update_placar_jogo
from Crud.Delete.delete_queries import delete_golos_por_jogo, delete_jogo


def listar_jogos() -> None:
    jogos = select_todos_jogos()
    print("\n" + "-" * 65)
    print("CALENDÁRIO E RESULTADOS DA LIGA")
    print("-" * 65)
    if not jogos:
        print("Ainda não existem jogos registados na liga.")
    else:
        for id_jogo, data, eq_casa, eq_fora, g_casa, g_fora in jogos:
            str_g_casa = g_casa if g_casa is not None else "-"
            str_g_fora = g_fora if g_fora is not None else "-"
            print(f"ID: {id_jogo:<3} | Data: {data} | {eq_casa} {str_g_casa}-{str_g_fora} {eq_fora}")
    print("-" * 65)


def inserir_jogo() -> None:
    print("\n-- INSERIR NOVO JOGO --")
    data = input("Data (YYYY-MM-DD): ").strip()
    local = input("Local (Ex: Estádio da Luz): ").strip()

    equipas = select_todas_equipas()
    print("\nEquipas Disponíveis:")
    for id_equipa, nome, _ in equipas:
        print(f"ID {id_equipa}: {nome}")

    id_casa = input("\nID da Equipa da Casa: ").strip()
    id_fora = input("ID da Equipa de Fora: ").strip()

    if id_casa == id_fora:
        print("Erro: A equipa da casa não pode ser a mesma que a equipa de fora!")
        return

    input_g_casa = input("Golos Casa (Deixa em branco se ainda não aconteceu): ").strip()
    input_g_fora = input("Golos Fora (Deixa em branco se ainda não aconteceu): ").strip()

    try:
        g_casa = int(input_g_casa) if input_g_casa else None
        g_fora = int(input_g_fora) if input_g_fora else None
    except ValueError:
        print("Erro: Os IDs das equipas e os golos devem ser números inteiros!")
        return

    if insert_jogo(data, local, id_casa, id_fora, g_casa, g_fora):
        print("Sucesso: Novo jogo inserido na liga!")
        registar_log("auditoria_jogos.log", "INSERÇÃO", f"Jogo inserido: Equipa {id_casa} vs Equipa {id_fora}")


def atualizar_placar() -> None:
    listar_jogos()
    id_jogo = input("\nDigita o ID do jogo para atualizar o placar (ou 0 para cancelar): ").strip()
    if id_jogo == '0':
        return

    input_g_casa = input("Novos golos da equipa da casa: ").strip()
    input_g_fora = input("Novos golos da equipa de fora: ").strip()

    try:
        g_casa = int(input_g_casa)
        g_fora = int(input_g_fora)
    except ValueError:
        print("Erro: O placar deve conter apenas valores numéricos!")
        return

    if not select_jogo_por_id(id_jogo):
        print("Erro: O ID do jogo fornecido não existe.")
        return

    if update_placar_jogo(id_jogo, g_casa, g_fora):
        print("Sucesso: Placar atualizado de forma oficial!")
        registar_log("auditoria_jogos.log", "ALTERAÇÃO", f"Placar do jogo ID {id_jogo} atualizado para {g_casa}-{g_fora}")


def remover_jogo() -> None:
    listar_jogos()
    id_jogo = input("\nDigita o ID do jogo que pretendes remover (ou 0 para cancelar): ").strip()
    if id_jogo == '0':
        return

    if not select_jogo_por_id(id_jogo):
        print("Erro: O ID do jogo fornecido não existe.")
        return

    delete_golos_por_jogo(id_jogo)
    if delete_jogo(id_jogo):
        print(f"Sucesso: O jogo ID {id_jogo} e os seus eventos foram removidos!")
        registar_log("auditoria_jogos.log", "REMOÇÃO", f"Jogo ID {id_jogo} apagado do sistema.")


def menu_gerir_jogos() -> None:
    while True:
        print("\n=== GERIR JOGOS ===")
        print("1. Listar todos os Jogos")
        print("2. Inserir Novo Jogo")
        print("3. Atualizar Placar de um Jogo")
        print("4. Remover Jogo")
        print("5. Voltar ao Painel Geral")
        escolha = input("Opção: ").strip()
        if escolha == '1':   listar_jogos()
        elif escolha == '2': inserir_jogo()
        elif escolha == '3': atualizar_placar()
        elif escolha == '4': remover_jogo()
        elif escolha == '5': break
        else:                print("Opção inválida!")
