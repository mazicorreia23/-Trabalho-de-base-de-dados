from Crud.Select.categorias.select_subconsultas import (
    select_jogadores_acima_media,
    select_equipas_que_nunca_ganharam,
)


def mostrar_jogadores_acima_media() -> None:
    resultados = select_jogadores_acima_media()
    print("\n--- JOGADORES ACIMA DA MÉDIA DE GOLOS ---")
    if not resultados:
        print("Não há dados suficientes.")
    else:
        for nome, equipa, total in resultados:
            print(f"  {nome} ({equipa}) - {total} Golos")


def mostrar_equipas_sem_vitoria() -> None:
    resultados = select_equipas_que_nunca_ganharam()
    print("\n--- EQUIPAS QUE NUNCA GANHARAM ---")
    if not resultados:
        print("Todas as equipas já ganharam pelo menos um jogo.")
    else:
        for (nome,) in resultados:
            print(f"  {nome}")


def menu_subconsultas(id_user: int, registar_cobrar) -> None:
    while True:
        print("""
            *** 5. SUBCONSULTAS ***
            1- Jogadores acima da média de golos
            2- Equipas que nunca ganharam nenhuma partida
            3- Voltar ao Menu Principal
        """)
        try:
            match int(input("Escolha uma opção\n=> ")):
                case 1:
                    mostrar_jogadores_acima_media()
                    registar_cobrar(id_user, 6)
                    input("\nPressione Enter para continuar...")
                case 2:
                    mostrar_equipas_sem_vitoria()
                    registar_cobrar(id_user, 18)
                    input("\nPressione Enter para continuar...")
                case 3:
                    break
                case _:
                    print("Escolha uma opção válida.")
        except ValueError:
            print("Por favor, introduza um número válido.")
