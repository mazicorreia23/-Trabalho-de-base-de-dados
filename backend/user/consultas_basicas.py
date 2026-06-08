from Crud.Select.categorias.select_basicas import (
    select_equipas_nome_cidade,
    select_jogadores_por_equipa_nome,
    select_todas_partidas_com_local,
    select_todos_utilizadores,
)


def mostrar_equipas() -> None:
    resultados = select_equipas_nome_cidade()
    print("\n--- LISTA DE EQUIPAS ---")
    if not resultados:
        print("Não há equipas registadas.")
    else:
        for nome, cidade in resultados:
            print(f"  {nome} ({cidade or 'N/D'})")


def mostrar_jogadores_equipa() -> bool:
    """Devolve False se o utilizador cancelou (input vazio), True caso contrário."""
    nome = input("\nDigita o nome (ou parte) da equipa: ").strip()
    if not nome:
        print("Operação cancelada.")
        return False
    resultados = select_jogadores_por_equipa_nome(nome)
    print(f"\n--- JOGADORES DA EQUIPA '{nome.upper()}' ---")
    if not resultados:
        print("Nenhum jogador encontrado para essa equipa.")
    else:
        for j_nome, posicao, idade in resultados:
            print(f"  {j_nome} | Posição: {posicao} | Idade: {idade or 'N/D'}")
    return True


def mostrar_todas_partidas() -> None:
    resultados = select_todas_partidas_com_local()
    print("\n--- TODAS AS PARTIDAS ---")
    if not resultados:
        print("Nenhuma partida registada.")
    else:
        print(f"{'DATA':<12} | {'LOCAL':<20} | {'CASA':<18} | {'FORA':<18} | PLACAR")
        print("-" * 80)
        for data, local, e1, e2, gc, gf in resultados:
            print(f"{data:<12} | {local[:18]:<20} | {e1[:16]:<18} | {e2[:16]:<18} | {gc}-{gf}")


def mostrar_todos_utilizadores() -> None:
    resultados = select_todos_utilizadores()
    print("\n--- UTILIZADORES CADASTRADOS ---")
    if not resultados:
        print("Nenhum utilizador registado.")
    else:
        for id_u, conta in resultados:
            print(f"  ID {id_u}: {conta}")


def menu_consultas_basicas(id_user: int, registar_cobrar) -> None:
    while True:
        print("""
            *** 1. CONSULTAS BÁSICAS ***
            1- Listar todas as equipas
            2- Mostrar jogadores de uma equipa específica
            3- Exibir todas as partidas (data, local, times)
            4- Listar todos os utilizadores cadastrados
            5- Voltar ao Menu Principal
        """)
        try:
            match int(input("Escolha uma opção\n=> ")):
                case 1:
                    mostrar_equipas()
                    registar_cobrar(id_user, 1)
                    input("\nPressione Enter para continuar...")
                case 2:
                    executou = mostrar_jogadores_equipa()
                    if executou:
                        registar_cobrar(id_user, 8)
                        input("\nPressione Enter para continuar...")
                case 3:
                    mostrar_todas_partidas()
                    registar_cobrar(id_user, 9)
                    input("\nPressione Enter para continuar...")
                case 4:
                    mostrar_todos_utilizadores()
                    registar_cobrar(id_user, 22)  # id_tipo correto para "Listar utilizadores"
                    input("\nPressione Enter para continuar...")
                case 5:
                    break
                case _:
                    print("Escolha uma opção válida.")
        except ValueError:
            print("Por favor, introduza um número válido.")
