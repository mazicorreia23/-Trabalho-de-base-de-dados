from typing import Optional

from Crud.Select.categorias.select_financas import (
    select_tipo_consulta_por_id,
    select_ids_tipos_consulta_existentes,
)
from Crud.Select.categorias.select_joins import select_historico_consultas
from Crud.Select.categorias.select_basicas import select_id_utilizador
from Crud.Insert.insert_queries import insert_consulta, insert_tipo_consulta_individual

from backend.user.consultas_basicas   import menu_consultas_basicas
from backend.user.filtragem_ordenacao import menu_filtragem_ordenacao
from backend.user.consultas_joins     import menu_joins
from backend.user.agregacao           import menu_agregacao
from backend.user.subconsultas        import menu_subconsultas
from backend.user.consultas_avancadas import menu_consultas_avancadas


# ---------------------------------------------------------------------------
# TIPOS DE CONSULTA - IDs mapeados
# ---------------------------------------------------------------------------
# 1  - Listar todas as equipas           | 2  - Jogadores com +5 Golos
# 3  - Top 5 Artilheiros (RANK)          | 4  - Equipas Invictas
# 5  - Pesquisa Curinga                  | 6  - Jogadores Acima da Média
# 7  - Jogos acima da Média de Golos     | 8  - Jogadores de uma equipa específica
# 9  - Todas as partidas (data/local)    | 10 - Partidas por local
# 11 - Marcadores de uma partida         | 12 - Todas as partidas com placar
# 13 - Golos de uma partida detalhado    | 14 - Golos do jogador X
# 15 - Artilharia da liga                | 16 - Total golos por equipa
# 17 - Partidas por equipa               | 18 - Equipas que nunca ganharam
# 19 - Jogos com vencedor                | 20 - Utilizadores por período
# 21 - Custo total por utilizador        | 22 - Listar todos os utilizadores


def _garantir_tipos_consulta() -> None:
    """Insere na BD os tipos de consulta que ainda não existam."""
    TODOS_OS_TIPOS = {
        1:  ('Listar todas as equipas (Básica)',           1.00),
        2:  ('Jogadores com +5 Golos (Filtragem)',         1.50),
        3:  ('Top 5 Artilheiros (RANK)',                   2.50),
        4:  ('Equipas Invictas (Subconsulta)',              3.00),
        5:  ('Pesquisa de Jogador por Nome (LIKE)',         1.00),
        6:  ('Jogadores Acima da Média de Golos',          3.50),
        7:  ('Jogos com Mais Golos que a Média',           3.50),
        8:  ('Jogadores de uma Equipa Específica',         1.50),
        9:  ('Todas as Partidas com Local',                1.00),
        10: ('Partidas por Local',                         1.50),
        11: ('Marcadores de uma Partida',                  1.50),
        12: ('Todas as Partidas com Placar',               1.00),
        13: ('Golos de uma Partida (Jogador + Equipa)',    2.00),
        14: ('Golos do Jogador X',                         1.50),
        15: ('Artilharia da Liga',                         2.00),
        16: ('Total de Golos por Equipa',                  2.00),
        17: ('Partidas por Equipa',                        2.00),
        18: ('Equipas que Nunca Ganharam',                 3.00),
        19: ('Jogos com Vencedor',                         2.00),
        20: ('Utilizadores por Período',                   2.00),
        21: ('Custo Total por Utilizador',                 2.50),
        22: ('Listar todos os Utilizadores (Básica)',      1.00),
    }
    existentes = select_ids_tipos_consulta_existentes()
    for id_tipo, (descricao, custo) in TODOS_OS_TIPOS.items():
        if id_tipo not in existentes:
            insert_tipo_consulta_individual(id_tipo, descricao, custo)


def _registar_cobrar(id_utilizador: int, id_tipo: int) -> None:
    """Regista a consulta no histórico e mostra o custo cobrado."""
    insert_consulta(id_utilizador, id_tipo)
    tipo = select_tipo_consulta_por_id(id_tipo)
    if tipo:
        print(f"\n[SISTEMA FINANCEIRO] Consulta: '{tipo[0]}' | Valor descontado: {tipo[1]:.2f}€")


# ---------------------------------------------------------------------------
# MENU PRINCIPAL DO UTILIZADOR
# ---------------------------------------------------------------------------

def arrancar_menu_user(conta_utilizador: str) -> None:
    _garantir_tipos_consulta()

    id_user = select_id_utilizador(conta_utilizador)
    if not id_user:
        print("\nErro Crítico: Não foi possível carregar o teu perfil. Contacta o administrador.")
        return

    while True:
        print("\n" + "=" * 58)
        print(f"   MENU DE CONSULTAS | Bem-vindo, {conta_utilizador}")
        print("=" * 58)
        print("1. Consultas Básicas          [1.00€ - 1.50€]")
        print("2. Filtragem e Ordenação      [1.00€ - 2.00€]")
        print("3. Consultas com JOINs        [1.00€ - 2.00€]")
        print("4. Agrupamento e Agregação    [1.50€ - 2.50€]")
        print("5. Subconsultas               [3.00€ - 3.50€]")
        print("6. Consultas Avançadas        [2.00€ - 3.50€]")
        print("\n--- GESTÃO DE CONTA ---")
        print("7. Ver o meu histórico e custo acumulado")
        print("8. Logout")

        match input("Escolhe uma opção: ").strip():
            case '1': menu_consultas_basicas(id_user, _registar_cobrar)
            case '2': menu_filtragem_ordenacao(id_user, _registar_cobrar)
            case '3': menu_joins(id_user, conta_utilizador, _registar_cobrar)
            case '4': menu_agregacao(id_user, _registar_cobrar)
            case '5': menu_subconsultas(id_user, _registar_cobrar)
            case '6': menu_consultas_avancadas(id_user, _registar_cobrar)
            case '7':
                resultados = select_historico_consultas(id_user)
                print("\n" + "=" * 80)
                print(f"   A TUA CONTA: HISTÓRICO E DÍVIDA ({conta_utilizador.upper()})")
                print("=" * 80)
                if not resultados:
                    print("Ainda não realizaste consultas pagas.")
                else:
                    print(f"{'DATA/HORA':<20} | {'DESCRIÇÃO':<35} | {'CUSTO':<6} | {'DÍVIDA TOTAL'}")
                    print("-" * 80)
                    for data, descricao, custo, acumulado in resultados:
                        print(f"{data:<20} | {descricao[:33]:<35} | {custo:>5.2f}€ | {acumulado:>9.2f}€")
            case '8':
                print(f"\nSessão terminada. Obrigado pela preferência, {conta_utilizador}!")
                break
            case _:
                print("Opção inválida! Escolhe um número de 1 a 8.")
