from Crud.Select.categorias.select_agregacao import (
    select_golos_por_jogador,
    select_artilharia_liga,
    select_total_golos_por_equipa,
    select_custo_total_por_utilizador,
    select_partidas_por_equipa,
)


def mostrar_golos_jogador_x() -> bool:
    """Devolve False se cancelado, True caso contrário."""
    nome = input("\nDigita o nome (ou parte) do jogador: ").strip()
    if not nome:
        print("Operação cancelada.")
        return False
    resultados = select_golos_por_jogador(nome)
    print(f"\n--- GOLOS DE '{nome.upper()}' ---")
    if not resultados:
        print("Nenhum jogador encontrado.")
    else:
        for j_nome, equipa, total in resultados:
            print(f"  {j_nome} ({equipa}) — {total} golo(s)")
    return True


def mostrar_artilharia_liga() -> None:
    resultados = select_artilharia_liga()
    print("\n--- ARTILHARIA DA LIGA ---")
    if not resultados:
        print("Sem dados suficientes.")
    else:
        for nome, equipa, total in resultados:
            print(f"  {nome} ({equipa}) — {total} golos")


def mostrar_total_golos_por_equipa() -> None:
    resultados = select_total_golos_por_equipa()
    print("\n--- TOTAL DE GOLOS POR EQUIPA ---")
    if not resultados:
        print("Sem dados.")
    else:
        for nome, total in resultados:
            print(f"  {nome}: {total} golo(s)")


def mostrar_custo_total_por_utilizador() -> None:
    resultados = select_custo_total_por_utilizador()
    print("\n--- CUSTO TOTAL POR UTILIZADOR ---")
    if not resultados:
        print("Sem consultas registadas.")
    else:
        for conta, total in resultados:
            print(f"  {conta}: {total:.2f}€")


def mostrar_partidas_por_equipa() -> None:
    resultados = select_partidas_por_equipa()
    print("\n--- PARTIDAS POR EQUIPA ---")
    if not resultados:
        print("Sem dados.")
    else:
        for nome, total in resultados:
            print(f"  {nome}: {total} partida(s)")


def menu_agregacao(id_user: int, registar_cobrar) -> None:
    while True:
        print("""
            *** 4. AGRUPAMENTO E AGREGAÇÃO ***
            1- Quantos golos marcou o jogador X?
            2- Artilharia da liga (jogador com mais golos)
            3- Total de golos marcados por cada equipa
            4- Custo total das consultas por utilizador
            5- Quantidade de partidas por equipa
            6- Voltar ao Menu Principal
        """)
        try:
            match int(input("Escolha uma opção\n=> ")):
                case 1:
                    if mostrar_golos_jogador_x():
                        registar_cobrar(id_user, 14)
                        input("\nPressione Enter para continuar...")
                case 2:
                    mostrar_artilharia_liga()
                    registar_cobrar(id_user, 15)
                    input("\nPressione Enter para continuar...")
                case 3:
                    mostrar_total_golos_por_equipa()
                    registar_cobrar(id_user, 16)
                    input("\nPressione Enter para continuar...")
                case 4:
                    mostrar_custo_total_por_utilizador()
                    registar_cobrar(id_user, 21)
                    input("\nPressione Enter para continuar...")
                case 5:
                    mostrar_partidas_por_equipa()
                    registar_cobrar(id_user, 17)
                    input("\nPressione Enter para continuar...")
                case 6:
                    break
                case _:
                    print("Escolha uma opção válida.")
        except ValueError:
            print("Por favor, introduza um número válido.")
