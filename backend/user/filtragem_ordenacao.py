from Crud.Select.categorias.select_filtragem_ordenacao import (
    select_jogadores_mais_5_golos,
    select_jogadores_curinga,
    select_partidas_por_local,
    select_utilizadores_por_periodo,
)
from Crud.Select.categorias.select_joins import select_jogadores_que_marcaram_em_jogo


def mostrar_partidas_por_local() -> bool:
    """Devolve False se cancelado, True caso contrário."""
    local = input("\nDigita o local a pesquisar: ").strip()
    if not local:
        print("Operação cancelada.")
        return False
    resultados = select_partidas_por_local(local)
    print(f"\n--- PARTIDAS EM '{local.upper()}' ---")
    if not resultados:
        print("Nenhuma partida encontrada nesse local.")
    else:
        for data, loc, e1, e2, gc, gf in resultados:
            print(f"  {data} | {loc} | {e1} {gc}-{gf} {e2}")
    return True


def mostrar_marcadores_jogo() -> bool:
    """Devolve False se cancelado, True caso contrário."""
    entrada = input("\nDigita o ID do jogo: ").strip()
    if not entrada:
        print("Operação cancelada.")
        return False
    try:
        id_jogo = int(entrada)
    except ValueError:
        print("ID inválido.")
        return False
    resultados = select_jogadores_que_marcaram_em_jogo(id_jogo)
    print(f"\n--- MARCADORES DO JOGO #{id_jogo} ---")
    if not resultados:
        print("Nenhum golo registado nesse jogo (ou jogo inexistente).")
    else:
        for j_nome, equipa, minuto in resultados:
            print(f"  {minuto}' | {j_nome} ({equipa})")
    return True


def mostrar_jogadores_mais_5_golos() -> None:
    resultados = select_jogadores_mais_5_golos()
    print("\n--- JOGADORES COM MAIS DE 5 GOLOS ---")
    if not resultados:
        print("Nenhum jogador atingiu esta marca ainda.")
    else:
        for nome, equipa, total in resultados:
            print(f"  {nome} ({equipa}) - {total} Golos")


def mostrar_pesquisa_curinga() -> bool:
    """Devolve False se cancelado, True caso contrário."""
    nome = input("\nDigita parte do nome do jogador: ").strip()
    if not nome:
        print("Operação cancelada.")
        return False
    resultados = select_jogadores_curinga(nome)
    print(f"\n--- RESULTADOS PARA '{nome}' ---")
    if not resultados:
        print("Nenhum jogador encontrado.")
    else:
        for j_nome, posicao, equipa in resultados:
            print(f"  {j_nome} | Posição: {posicao} | Equipa: {equipa}")
    return True


def mostrar_utilizadores_por_periodo() -> bool:
    """Devolve False se cancelado, True caso contrário."""
    print("\n  Formato da data: AAAA-MM-DD HH:MM:SS  (ex: 2025-01-01 00:00:00)")
    data_inicio = input("  Data início: ").strip()
    data_fim    = input("  Data fim:    ").strip()
    if not data_inicio or not data_fim:
        print("Operação cancelada.")
        return False
    resultados = select_utilizadores_por_periodo(data_inicio, data_fim)
    print(f"\n--- UTILIZADORES COM CONSULTAS ENTRE {data_inicio} E {data_fim} ---")
    if not resultados:
        print("Nenhuma consulta registada nesse período.")
    else:
        for conta, total in resultados:
            print(f"  {conta} — {total} consulta(s)")
    return True


def menu_filtragem_ordenacao(id_user: int, registar_cobrar) -> None:
    while True:
        print("""
            *** 2. FILTRAGEM E ORDENAÇÃO ***
            1- Partidas realizadas num determinado local
            2- Jogadores que marcaram numa partida específica
            3- Jogadores com mais de 5 golos (Ordem Decrescente)
            4- Pesquisar jogador por nome (Curinga)
            5- Utilizadores que consultaram num período específico
            6- Voltar ao Menu Principal
        """)
        try:
            match int(input("Escolha uma opção\n=> ")):
                case 1:
                    if mostrar_partidas_por_local():
                        registar_cobrar(id_user, 10)
                        input("\nPressione Enter para continuar...")
                case 2:
                    if mostrar_marcadores_jogo():
                        registar_cobrar(id_user, 11)
                        input("\nPressione Enter para continuar...")
                case 3:
                    mostrar_jogadores_mais_5_golos()
                    registar_cobrar(id_user, 2)
                    input("\nPressione Enter para continuar...")
                case 4:
                    if mostrar_pesquisa_curinga():
                        registar_cobrar(id_user, 5)
                        input("\nPressione Enter para continuar...")
                case 5:
                    if mostrar_utilizadores_por_periodo():
                        registar_cobrar(id_user, 20)
                        input("\nPressione Enter para continuar...")
                case 6:
                    break
                case _:
                    print("Escolha uma opção válida.")
        except ValueError:
            print("Por favor, introduza um número válido.")
