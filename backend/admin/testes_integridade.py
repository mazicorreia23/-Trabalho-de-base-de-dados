from Crud.Select.categorias.select_integridade import (
    select_jogos_golos_negativos,
    select_golos_minutos_invalidos,
    select_jogadores_sem_equipa,
    select_jogos_equipa_contra_si,
)


def correr_testes_integridade() -> None:
    print("\n" + "=" * 55)
    print("A CORRER TESTES DE INTEGRIDADE DOS DADOS")
    print("=" * 55)

    erros_encontrados = 0

    # Teste 1: golos negativos
    jogos_invalidos = select_jogos_golos_negativos()
    if jogos_invalidos:
        print(f"FALHA: Encontrados {len(jogos_invalidos)} jogos com golos negativos!")
        erros_encontrados += 1
    else:
        print("PASSOU: Nenhum jogo tem golos negativos.")

    # Teste 2: minutos inválidos
    golos_invalidos = select_golos_minutos_invalidos()
    if golos_invalidos:
        print(f"FALHA: Encontrados {len(golos_invalidos)} golos em minutos absurdos!")
        erros_encontrados += 1
    else:
        print("PASSOU: Todos os golos têm minutos válidos.")

    # Teste 3: jogadores órfãos
    jogadores_orfaos = select_jogadores_sem_equipa()
    if jogadores_orfaos:
        print(f"FALHA: Encontrados {len(jogadores_orfaos)} jogadores sem equipa!")
        erros_encontrados += 1
    else:
        print("PASSOU: Todos os jogadores pertencem a uma equipa.")

    # Teste 4: equipa contra si mesma
    jogos_espelho = select_jogos_equipa_contra_si()
    if jogos_espelho:
        print(f"FALHA: Encontrados {len(jogos_espelho)} jogos onde uma equipa joga contra si mesma!")
        erros_encontrados += 1
    else:
        print("PASSOU: Nenhuma equipa joga contra si própria na liga.")

    print("-" * 55)
    if erros_encontrados > 0:
        print(f"ATENÇÃO: Foram detetados {erros_encontrados} problemas de integridade!")
    else:
        print("SUCESSO: Base de dados validada sem anomalias detetadas.")
    print("-" * 55)
