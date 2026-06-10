from Crud.Select.categorias.select_avancadas import (
    select_top5_artilheiros,
    select_jogos_com_vencedor,
    select_equipas_invictas,
    select_jogos_acima_media_golos,
)


def mostrar_top5_artilheiros() -> None:
    resultados = select_top5_artilheiros()
    print("\n--- TOP 5 ARTILHEIROS (RANK) ---")
    if not resultados:
        print("Ainda não há golos suficientes para formar o ranking.")
    else:
        for nome, equipa, total, ranking in resultados:
            print(f"  #{ranking} | {nome} ({equipa}) - {total} Golos")


def mostrar_jogos_com_vencedor() -> None:
    resultados = select_jogos_com_vencedor()
    print("\n--- JOGOS COM VENCEDOR ---")
    if not resultados:
        print("Nenhum jogo com vencedor encontrado.")
    else:
        print(f"{'DATA':<12} | {'CASA':<16} | {'FORA':<16} | PLACAR | VENCEDOR")
        print("-" * 75)
        for data, casa, fora, gc, gf, vencedor in resultados:
            print(f"{data:<12} | {casa[:14]:<16} | {fora[:14]:<16} | {gc}-{gf}    | {vencedor}")


def mostrar_equipas_invictas() -> None:
    resultados = select_equipas_invictas()
    print("\n--- EQUIPAS INVICTAS (nunca perderam) ---")
    if not resultados:
        print("Nenhuma equipa está invicta.")
    else:
        for (nome,) in resultados:
            print(f"  {nome}")


def mostrar_jogos_acima_media() -> None:
    resultados = select_jogos_acima_media_golos()
    print("\n--- JOGOS COM GOLOS ACIMA DA MÉDIA ---")
    if not resultados:
        print("Não há jogos suficientes para calcular esta métrica.")
    else:
        for e1, e2, g_casa, g_fora, total in resultados:
            print(f"  {e1} {g_casa}-{g_fora} {e2} (Total: {total} golos)")


def menu_consultas_avancadas(id_user: int, registar_cobrar) -> None:
    while True:
        print("""
            *** 6. CONSULTAS AVANÇADAS ***
            1- Top 5 Artilheiros (com RANK)
            2- Jogos com vencedor (sem empate)
            3- Equipas Invictas (nunca perderam)
            4- Jogos com mais golos que a média
            5- Voltar ao Menu Principal
        """)
        try:
            match int(input("Escolha uma opção\n=> ")):
                case 1:
                    mostrar_top5_artilheiros()
                    registar_cobrar(id_user, 3)
                    input("\nPressione Enter para continuar...")
                case 2:
                    mostrar_jogos_com_vencedor()
                    registar_cobrar(id_user, 19)
                    input("\nPressione Enter para continuar...")
                case 3:
                    mostrar_equipas_invictas()
                    registar_cobrar(id_user, 4)
                    input("\nPressione Enter para continuar...")
                case 4:
                    mostrar_jogos_acima_media()
                    registar_cobrar(id_user, 7)
                    input("\nPressione Enter para continuar...")
                case 5:
                    break
                case _:
                    print("Escolha uma opção válida.")
        except ValueError:
            print("Por favor, introduza um número válido.")
