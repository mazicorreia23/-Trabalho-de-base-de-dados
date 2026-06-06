# Importa a função 'conectar' do módulo local 'backend.database' para permitir o acesso programático à base de dados SQLite.
from backend.database import conectar

def correr_testes_integridade() -> None:
    """
    Varre a base de dados à procura de anomalias lógicas e 
    falhas de integridade referencial.
    """
    # Imprime um cabeçalho visual no terminal para indicar o início do processo de auditoria de dados.
    print("\n" + "="*55)
    print("A CORRER TESTES DE INTEGRIDADE DOS DADOS")
    print("="*55)
    
    # Estabelece a ligação à base de dados chamando a função importada.
    conn = conectar()
    # Se a ligação falhar (devolver None), interrompe o teste e avisa o utilizador.
    if not conn:
        print("Erro Crítico: Não foi possível ligar à base de dados para correr os testes.")
        return

    # Inicializa um contador para registar o número total de falhas lógicas encontradas durante a auditoria.
    erros_encontrados = 0
    
    try:
        # Cria um objeto cursor para poder enviar comandos SQL para o motor da base de dados.
        cursor = conn.cursor()
        
        # Teste 1: Verificação de valores matemáticos impossíveis no placar.
        # Executa uma consulta à tabela 'jogo' para encontrar registos onde o número de golos seja inferior a zero.
        cursor.execute("SELECT id_jogo FROM jogo WHERE golos_casa < 0 OR golos_fora < 0")
        # Guarda todos os resultados suspeitos numa lista.
        jogos_invalidos = cursor.fetchall()
        # Se a lista contiver elementos, significa que houve falha no teste de integridade.
        if jogos_invalidos:
            print(f"FALHA: Encontrados {len(jogos_invalidos)} jogos com golos negativos!")
            erros_encontrados += 1
        else:
            # Caso contrário, o teste é considerado bem-sucedido.
            print("PASSOU: Nenhum jogo tem golos negativos.")
            
        # Teste 2: Verificação de cronometragem desportiva.
        # Pesquisa na tabela 'golo' por ocorrências registadas fora do intervalo de tempo plausível de uma partida (1 a 130 minutos).
        cursor.execute("SELECT id_golo FROM golo WHERE minuto < 1 OR minuto > 130")
        golos_invalidos = cursor.fetchall()
        if golos_invalidos:
            print(f"FALHA: Encontrados {len(golos_invalidos)} golos em minutos absurdos!")
            erros_encontrados += 1
        else:
            print("PASSOU: Todos os golos têm minutos válidos.")
            
        # Teste 3: Deteção de registos "órfãos" (falha de associação).
        # Procura jogadores que, por erro de inserção ou remoção, não estejam vinculados a nenhuma equipa (ID de equipa nulo).
        cursor.execute("SELECT id_jogador FROM jogador WHERE id_equipa IS NULL")
        jogadores_orfaos = cursor.fetchall()
        if jogadores_orfaos:
            print(f"FALHA: Encontrados {len(jogadores_orfaos)} jogadores sem equipa!")
            erros_encontrados += 1
        else:
            print("PASSOU: Todos os jogadores pertencem a uma equipa.")
            
        # Teste 4 [NOVO]: Validação de regras de competição.
        # Verifica se existem jogos registados onde o ID da equipa visitada é idêntico ao ID da equipa visitante, o que seria logicamente impossível.
        cursor.execute("SELECT id_jogo FROM jogo WHERE id_equipa_casa = id_equipa_fora")
        jogos_espelho = cursor.fetchall()
        if jogos_espelho:
            print(f"FALHA: Encontrados {len(jogos_espelho)} jogos onde uma equipa joga contra si mesma!")
            erros_encontrados += 1
        else:
            print("PASSOU: Nenhuma equipa joga contra si própria na liga.")
            
    except Exception as e:
        # Captura e exibe qualquer erro técnico inesperado que ocorra durante as consultas SQL.
        print(f"Erro inesperado durante a execução dos testes: {e}")
    finally:
        # Garante que a ligação à base de dados é encerrada corretamente no final, independentemente de terem ocorrido erros ou não.
        conn.close()
        
    # Imprime uma linha de separação final.
    print("-" * 55)
    # Se o contador for superior a zero, emite um aviso de atenção.
    if erros_encontrados > 0:
        print(f"ATENÇÃO: Foram detetados {erros_encontrados} problemas de integridade!")
    else:
        # Caso o sistema esteja limpo de erros lógicos.
        print("SUCESSO: Base de dados validada sem anomalias detetadas.")
    print("-" * 55)