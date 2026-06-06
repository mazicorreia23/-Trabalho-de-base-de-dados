# Importa a função 'conectar' do módulo 'backend.database' pertencente ao projeto, que é usada para inicializar a ligação à base de dados.
from backend.database import conectar
# Importa a indicação de tipo 'Optional' do módulo nativo 'typing', útil para o Python perceber que uma variável ou retorno pode ser de um certo tipo ou simplesmente 'None' (vazio).
from typing import Optional

# Define a função responsável por listar as dívidas e o histórico de consultas de cada utilizador. A anotação '-> None' indica que a função apenas executa ações e não devolve (return) valores ao sistema.
def ver_dividas_usuarios() -> None:
    """
    O administrador visualiza a lista de consultas por utilizador com:
    Nome da consulta, Custo individual, Custo acumulado (ordenado por data).
    """
    # Invoca a função de ligação à base de dados e guarda o objeto de conexão resultante na variável 'conn'.
    conn = conectar()
    # Verifica se a ligação falhou (caso o 'conn' devolva None ou False). Se sim, aborta a execução saindo prematuramente da função.
    if not conn:
        return
        
    # Inicializa um objeto 'cursor', que atua como o mensageiro encarregue de transportar e executar as instruções SQL na base de dados conectada.
    cursor = conn.cursor()
    
    # A magia do SQL: A função SUM(...) OVER (...) cria a coluna de custo acumulado linha a linha!
    # Variável 'query' armazena o comando SQL em formato de texto.
    # - O comando agrupa os dados do utilizador e a descrição da consulta juntando tabelas ('JOIN').
    # - A função avançada 'SUM() OVER (PARTITION BY ...)' faz o cálculo contínuo do custo. Para cada utilizador, vai somando os valores em ordem cronológica (criando uma espécie de extrato de dívida progressiva).
    # - O filtro 'WHERE' garante que o próprio utilizador administrador seja excluído da contabilidade financeira.
    query = """
    SELECT 
        u.conta, 
        c.data_hora, 
        t.descricao, 
        t.custo,
        SUM(t.custo) OVER (PARTITION BY u.id_utilizador ORDER BY c.data_hora) as custo_acumulado
    FROM utilizador u
    JOIN consulta c ON u.id_utilizador = c.id_utilizador
    JOIN tipo_consulta t ON c.id_tipo = t.id_tipo
    WHERE u.conta != 'admin'
    ORDER BY u.conta, c.data_hora;
    """
    
    # Inicia um bloco 'try' para proteger o código. Se ocorrerem falhas inesperadas de comunicação na leitura da base de dados, o programa salta para o 'except' em vez de "crashar".
    try:
        # Envia a string com a instrução SQL guardada na variável 'query' para o motor SQLite executar.
        cursor.execute(query)
        # O método 'fetchall()' extrai todas as linhas resultantes da consulta efetuada e guarda-as numa lista de tuplos na variável 'resultados'.
        resultados = cursor.fetchall()
        
        # Imprime no ecrã (consola) uma quebra de linha seguida de 85 barras horizontais ('=') para criar as margens do cabeçalho visual do relatório.
        print("\n" + "="*85)
        # Apresenta o título principal do documento gerado no ecrã.
        print("RELATÓRIO FINANCEIRO: DÍVIDAS E HISTÓRICO DE UTILIZADORES")
        # Fecha a caixa do cabeçalho com mais 85 sinais de igualdade.
        print("="*85)
        
        # Valida se a base de dados não devolveu nada (ou seja, se a lista de 'resultados' está vazia).
        if not resultados:
            # Se a lista estiver vazia, imprime uma mensagem a informar o utilizador do motivo de não haver listagens.
            print("Nenhum utilizador realizou consultas pagas até ao momento.")
        # Caso contrário, havendo dados para mostrar, procede com o ciclo de listagem.
        else:
            # Cria a variável de controlo 'utilizador_atual'. Vai servir para monitorizar o momento em que o código passa de ler os registos do "Utilizador A" para o "Utilizador B".
            utilizador_atual = ""
            # Ciclo 'for' que varre uma a uma todas as linhas (tuplos) obtidas da base de dados.
            for linha in resultados:
                # Desempacotar o tuplo diretamente torna o código mais Pythonic
                # Distribui cada um dos cinco elementos devolvidos no tuplo do SQL pelas respetivas variáveis Python de forma sequencial.
                conta, data, consulta, custo, acumulado = linha
                
                # Estética: Quando muda o utilizador, imprimimos um novo cabeçalho
                # Condição que é acionada sempre que se lida com os dados de um novo cliente face à linha lida anteriormente.
                if conta != utilizador_atual:
                    # Se não for o primeiro da lista, desenha uma linha separadora fina ('-') para distinguir visualmente onde termina um cliente e começa o próximo.
                    if utilizador_atual != "":
                        print("-" * 85) # Linha divisória antes do próximo utilizador
                        
                    # Imprime o nome de conta do utilizador destacado com letras maiúsculas através do '.upper()'.
                    print(f"\nUTILIZADOR: {conta.upper()}")
                    # Imprime os cabeçalhos das colunas alinhados à esquerda (símbolo '<') usando um espaçamento pré-definido por caracteres para simular o aspeto de grelha de tabela.
                    print(f"{'DATA/HORA':<20} | {'CONSULTA':<38} | {'CUSTO':<6} | {'ACUMULADO':<10}")
                    # Linha pontilhada de remate para o subcabeçalho de colunas.
                    print("-" * 85)
                    # Atualiza o identificador da variável de controlo para a iteração seguinte saber de quem são os dados correntes.
                    utilizador_atual = conta
                    
                # Imprime a linha de cada consulta com formatação alinhada
                # Usa 'f-strings' para forçar a tabulação. As setas ('<' e '>') definem o alinhamento esquerdo e direito respetivamente. 'consulta[:35]' trunca propositadamente o nome demasiado longo da consulta aos 35 caracteres para evitar deformar a tabela. Os números ('custo' e 'acumulado') são impressos com 2 casas decimais e o símbolo de Euro.
                print(f"{data:<20} | {consulta[:35]:<38} | {custo:>5.2f}€ | {acumulado:>8.2f}€")
                
    # Zona de captura de falhas ou exceções ('Exceptions') do tipo técnico durante todo o bloco 'try'.
    except Exception as e:
        # Mostra amigavelmente no ecrã um aviso com o registo exato do erro ocorrido (variável 'e'), facilitando o diagnóstico informático (debugging).
        print(f"Erro ao carregar relatório financeiro: {e}")
    # O bloco 'finally' é obrigatório. Corre invariavelmente quer a leitura tenha sido um sucesso ou tenha resultado em erro.
    finally:
        # Encerra o canal de comunicação para que a base de dados não fique aberta ou bloqueada em memória indevidamente no sistema operativo.
        conn.close()
        # Coloca a orla inferior de fecho na interface gráfica de texto finalizando a tabela de resultados.
        print("="*85)
        
        # Chama automaticamente o resumo financeiro global no fim do relatório
        # Invoca agora a segunda função do script para acrescentar logo em baixo o somatório de ganhos de todos os utilizadores combinados.
        ver_receita_total()


# Função independente encarregue de somar apenas o total financeiro líquido apurado pela aplicação. Não devolve valores, apenas imprime.
def ver_receita_total() -> None:
    """
    Calcula e exibe a receita total gerada por todas as consultas 
    pagas de todos os utilizadores.
    """
    # Solicita nova instância de conexão à plataforma da base de dados.
    conn = conectar()
    # Sem ligação válida, interrompe imediatamente a operação de pesquisa em modo silencioso.
    if not conn:
        return
        
    # Recomeça o bloco de tentativa de comunicação protegida contra anomalias na leitura dos dados.
    try:
        # Declara o cursor em modo de execução nativa.
        cursor = conn.cursor()
        # Define numa query de linguagem SQL a instrução de efetuar uma soma matemática absoluta 'SUM(t.custo)' englobando todos os pagamentos efetuados, ignorando de novo a conta do técnico administrador.
        query = """
        SELECT SUM(t.custo) 
        FROM consulta c 
        JOIN tipo_consulta t ON c.id_tipo = t.id_tipo
        JOIN utilizador u ON c.id_utilizador = u.id_utilizador
        WHERE u.conta != 'admin'
        """
        # Desencadeia o pedido formulado acima no motor SQLite ativo.
        cursor.execute(query)
        # Diferente de 'fetchall', usa 'fetchone' porque a instrução SUM devolve apenas uma e uma única linha de resultado final. O index '[0]' tira apenas o valor isolado (o número exato do resultado da soma) de dentro do tuplo para o usar solto.
        resultado = cursor.fetchone()[0]
        
        # Se não houver consultas, o SUM devolve None. Passamos a 0.0.
        # Usa lógica do tipo condicional simplificada (operador ternário). Caso o resultado seja válido, assume-o. Se a instrução SUM SQL for alvo de tabela vazia e trouxer 'None' (nulo), ele é forçado a declarar 0.0 Euros de receita.
        total_global = resultado if resultado else 0.0
        
        # Imprime o lucro com duas casas fracionárias predefinidas por arredondamento visual ('.2f') para garantir precisão de cêntimos do Euro.
        print(f"\nRECEITA TOTAL ACUMULADA DA PLATAFORMA: {total_global:.2f}€")
        # Finaliza com mais uma barreira visual de equalização.
        print("="*85)
        
    # Interceta quebras do fluxo não deliberadas.
    except Exception as e:
        # Partilha no ecrã a indicação contextual de qual o erro encontrado que não permitiu chegar ao valor global total da plataforma.
        print(f"Erro ao calcular a receita total: {e}")
    # Encerramento garantido dos procedimentos.
    finally:
        # Fecho indispensável das portas com o ficheiro de persistência de dados do disco.
        conn.close()