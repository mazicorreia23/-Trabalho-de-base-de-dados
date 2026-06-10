from backend.admin.gerir_utilizadores import registar_log
from Crud.Select.categorias.select_basicas import (
    select_todas_equipas,
    select_equipa_por_id,
    select_todos_jogadores,
)
from Crud.Insert.insert_queries import insert_equipa, insert_jogador, insert_golo


def listar_equipas() -> None:
    equipas = select_todas_equipas()
    print("\n--- LISTA DE EQUIPAS ---")
    for id_eq, nome, cidade in equipas:
        print(f"ID: {id_eq:<3} | Nome: {nome:<20} | Cidade: {cidade or 'N/D'}")
    print("-" * 40)


def adicionar_equipa() -> None:
    print("\n-- ADICIONAR NOVA EQUIPA --")
    nome = input("Nome da Equipa: ").strip()
    if not nome:
        print("Erro: O nome da equipa é obrigatório!")
        return
    cidade = input("Cidade (opcional): ").strip() or None

    if insert_equipa(nome, cidade):
        print(f"Sucesso: Equipa '{nome}' registada!")
        registar_log("auditoria_jogos.log", "INSERÇÃO", f"Equipa '{nome}' adicionada ao sistema.")


def listar_jogadores() -> None:
    jogadores = select_todos_jogadores()
    print("\n--- LISTA DE JOGADORES ---")
    for id_jog, nome, posicao, equipa in jogadores:
        print(f"ID: {id_jog:<3} | {nome:<20} | Pos: {posicao:<10} | Equipa: {equipa}")
    print("-" * 55)


def adicionar_jogador() -> None:
    print("\n-- ADICIONAR NOVO JOGADOR --")
    nome = input("Nome do Jogador: ").strip()
    posicao = input("Posição (Ex: Avançado, Defesa): ").strip()
    if not nome or not posicao:
        print("Erro: O nome e a posição são obrigatórios!")
        return

    listar_equipas()
    id_equipa = input("\nID da Equipa a que o jogador pertence: ").strip()

    try:
        id_eq_int = int(id_equipa)
    except ValueError:
        print("Erro: O ID da equipa tem de ser um número inteiro!")
        return

    if not select_equipa_por_id(id_eq_int):
        print("Erro: ID de equipa inválido.")
        return

    if insert_jogador(nome, posicao, id_eq_int):
        print(f"Sucesso: Jogador '{nome}' registado!")
        registar_log("auditoria_jogos.log", "INSERÇÃO", f"Jogador '{nome}' associado à equipa ID {id_eq_int}.")


def registar_golo() -> None:
    print("\n-- REGISTAR NOVO GOLO --")
    from backend.admin.gerir_jogos import listar_jogos
    listar_jogos()

    id_jogo = input("\nID do Jogo onde o golo ocorreu (ou 0 para cancelar): ").strip()
    if id_jogo == '0' or not id_jogo:
        return

    listar_jogadores()
    id_jogador = input("\nID do Jogador que marcou: ").strip()
    minuto = input("Minuto do golo (1-130): ").strip()

    try:
        id_jg_int = int(id_jogo)
        id_jog_int = int(id_jogador)
        minuto_int = int(minuto)
    except ValueError:
        print("Erro: Os IDs e o minuto têm de ser números inteiros!")
        return

    if minuto_int < 1 or minuto_int > 130:
        print("Erro: Minuto inválido.")
        return

    if insert_golo(id_jg_int, id_jog_int, minuto_int):
        print(f"Sucesso: Golo registado ao minuto {minuto_int}!")
        registar_log("auditoria_jogos.log", "INSERÇÃO", f"Golo registado (Jogo: {id_jg_int}, Jogador: {id_jog_int}, Minuto: {minuto_int}).")


def menu_gestao_avancada() -> None:
    while True:
        print("\n=== GESTÃO AVANÇADA ===")
        print("1. Listar Equipas")
        print("2. Adicionar Equipa")
        print("3. Listar Jogadores")
        print("4. Adicionar Jogador")
        print("5. Registar Golo Individual")
        print("6. Voltar ao Painel Geral")
        escolha = input("Opção: ").strip()
        if escolha == '1':   listar_equipas()
        elif escolha == '2': adicionar_equipa()
        elif escolha == '3': listar_jogadores()
        elif escolha == '4': adicionar_jogador()
        elif escolha == '5': registar_golo()
        elif escolha == '6': break
        else:                print("Opção inválida!")
