from Crud.Select.categorias.select_joins import (
    select_jogos_com_placar,
    select_jogadores_que_marcaram_em_jogo,
    select_historico_consultas,
)
from Crud.Select.categorias.select_filtragem_ordenacao import select_jogadores_curinga


def mostrar_todas_partidas_placar() -> None:
    resultados = select_jogos_com_placar()
    print("\n--- PARTIDAS COM PLACAR ---")
    if not resultados:
        print("Nenhuma partida registada.")
    else:
        for e1, e2, gc, gf in resultados:
            print(f"  {e1}  {gc} - {gf}  {e2}")


def mostrar_golos_partida_detalhado() -> bool:
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
    print(f"\n--- GOLOS DO JOGO #{id_jogo} (Jogador + Equipa) ---")
    if not resultados:
        print("Sem golos registados (ou jogo inexistente).")
    else:
        for j_nome, equipa, minuto in resultados:
            print(f"  {minuto}' | {j_nome} ({equipa})")
    return True


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


def mostrar_historico_utilizador(id_utilizador: int, conta: str) -> None:
    resultados = select_historico_consultas(id_utilizador)
    print("\n" + "=" * 80)
    print(f"   HISTÓRICO DE CONSULTAS ({conta.upper()})")
    print("=" * 80)
    if not resultados:
        print("Ainda não realizaste consultas pagas.")
    else:
        print(f"{'DATA/HORA':<20} | {'DESCRIÇÃO':<35} | {'CUSTO':<6} | {'DÍVIDA TOTAL'}")
        print("-" * 80)
        for data, descricao, custo, acumulado in resultados:
            print(f"{data:<20} | {descricao[:33]:<35} | {custo:>5.2f}€ | {acumulado:>9.2f}€")


def menu_joins(id_user: int, conta: str, registar_cobrar) -> None:
    while True:
        print("""
            *** 3. CONSULTAS COM JOINS ***
            1- Todas as partidas com placar (nomes dos times)
            2- Golos de uma partida específica (jogador + equipa)
            3- Pesquisa curinga de jogador
            4- Histórico de consultas dos utilizadores
            5- Voltar ao Menu Principal
        """)
        try:
            match int(input("Escolha uma opção\n=> ")):
                case 1:
                    mostrar_todas_partidas_placar()
                    registar_cobrar(id_user, 12)
                    input("\nPressione Enter para continuar...")
                case 2:
                    if mostrar_golos_partida_detalhado():
                        registar_cobrar(id_user, 13)
                        input("\nPressione Enter para continuar...")
                case 3:
                    if mostrar_pesquisa_curinga():
                        registar_cobrar(id_user, 5)
                        input("\nPressione Enter para continuar...")
                case 4:
                    mostrar_historico_utilizador(id_user, conta)
                    input("\nPressione Enter para continuar...")
                case 5:
                    break
                case _:
                    print("Escolha uma opção válida.")
        except ValueError:
            print("Por favor, introduza um número válido.")
