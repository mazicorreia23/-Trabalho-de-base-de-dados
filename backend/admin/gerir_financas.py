from Crud.Select.categorias.select_financas import select_dividas_todos_utilizadores, select_receita_total


def ver_dividas_usuarios() -> None:
    """O administrador visualiza o relatório financeiro completo."""
    resultados = select_dividas_todos_utilizadores()

    print("\n" + "=" * 85)
    print("RELATÓRIO FINANCEIRO: DÍVIDAS E HISTÓRICO DE UTILIZADORES")
    print("=" * 85)

    if not resultados:
        print("Nenhum utilizador realizou consultas pagas até ao momento.")
    else:
        utilizador_atual = ""
        for conta, data, consulta, custo, acumulado in resultados:
            if conta != utilizador_atual:
                if utilizador_atual != "":
                    print("-" * 85)
                print(f"\nUTILIZADOR: {conta.upper()}")
                print(f"{'DATA/HORA':<20} | {'CONSULTA':<38} | {'CUSTO':<6} | {'ACUMULADO':<10}")
                print("-" * 85)
                utilizador_atual = conta
            print(f"{data:<20} | {consulta[:35]:<38} | {custo:>5.2f}€ | {acumulado:>8.2f}€")

    print("=" * 85)
    ver_receita_total()


def ver_receita_total() -> None:
    """Calcula e exibe a receita total gerada por todas as consultas pagas."""
    total_global = select_receita_total()
    print(f"\nRECEITA TOTAL ACUMULADA DA PLATAFORMA: {total_global:.2f}€")
    print("=" * 85)
