# Importa o módulo 'os', que permite interagir com as funcionalidades do sistema operativo.
import os
# Importa a classe 'datetime' para obtermos e formatarmos a data e a hora atuais do sistema.
from datetime import datetime
# Importa a anotação 'Optional' do módulo de tipagem, que indica que uma variável ou retorno pode ter um valor ou ser nula (None).
from typing import Optional
# Importa a função 'conectar' do ficheiro 'database.py' (dentro da pasta 'backend') para estabelecer a ligação à base de dados SQLite.
from backend.database import conectar


def obter_id_utilizador(conta: str) -> Optional[int]:
    """Devolve o ID do utilizador com base no nome da conta."""
    # Inicia a ligação à base de dados.
    conn = conectar()
    # Se não houver ligação (ex: erro no ficheiro da BD), a função devolve 'None' e termina.
    if not conn:
        return None
        
    # Inicia um bloco de tentativa ('try') para capturar e gerir possíveis erros durante a execução da consulta à base de dados.
    try:
        # Cria um cursor, que é o objeto responsável por executar as instruções SQL na base de dados.
        cursor = conn.cursor()
        # Executa uma consulta SQL para procurar o 'id_utilizador' na tabela 'utilizador' onde o nome da conta seja igual ao fornecido. O uso de '(conta,)' protege contra ataques de injeção SQL.
        cursor.execute("SELECT id_utilizador FROM utilizador WHERE conta = ?", (conta,))
        # Extrai o primeiro resultado encontrado e guarda-o na variável 'resultado'.
        resultado = cursor.fetchone()
        # Se encontrou um resultado, devolve o primeiro elemento do tuplo (que é o ID numérico). Se 'resultado' for vazio, devolve 'None'.
        return resultado[0] if resultado else None
    # Captura qualquer exceção não prevista.
    except Exception as e:
        # Imprime na consola a mensagem de erro técnico para ajudar na resolução de problemas (debugging).
        print(f"Erro ao obter ID do utilizador: {e}")
        # Retorna nulo em caso de falha.
        return None
    # O bloco 'finally' executa sempre no final, quer tenha ocorrido um erro ou não.
    finally:
        # Fecha a ligação à base de dados, libertando os recursos de memória do sistema.
        conn.close()


def garantir_tipos_consulta() -> None:
    """Insere os tipos de consulta e preços padrão se a tabela estiver vazia."""
    # Solicita a ligação à base de dados.
    conn = conectar()
    # Se falhar a ligação, aborta o processo de imediato.
    if not conn:
        return
        
    try:
        cursor = conn.cursor()
        # Conta quantas linhas existem atualmente na tabela 'tipo_consulta'.
        cursor.execute("SELECT COUNT(*) FROM tipo_consulta")
        
        # Se a contagem devolvida for zero (ou seja, a tabela está vazia e acabada de criar).
        if cursor.fetchone()[0] == 0:
            # Cria uma lista contendo múltiplos tuplos. Cada tuplo representa uma linha a ser inserida (Descrição da consulta e o respetivo Preço/Custo).
            precos = [
                ('Listar todas as equipas (Básica)', 1.00),
                ('Jogadores com +5 Golos (Filtragem)', 1.50),
                ('Top 5 Artilheiros (RANK)', 2.50),
                ('Equipas Invictas (Subconsulta)', 3.00),
                ('Pesquisa de Jogador por Nome (LIKE)', 1.00),
                ('Jogadores Acima da Média de Golos', 3.50),
                ('Jogos com Mais Golos que a Média', 3.50)
            ]
            # O comando 'executemany' é uma forma eficiente de executar o mesmo comando INSERT várias vezes consecutivas usando a lista de parâmetros 'precos'.
            cursor.executemany("INSERT INTO tipo_consulta (descricao, custo) VALUES (?, ?)", precos)
            # Confirma e guarda fisicamente as inserções no ficheiro da base de dados.
            conn.commit()
    except Exception as e:
        # Em caso de erro (ex: tabela não existe), avisa na consola.
        print(f"Erro ao inicializar preços das consultas: {e}")
    finally:
        # Garante sempre o encerramento da porta de comunicação com o SQLite.
        conn.close()


def registar_cobrar_consulta(id_utilizador: int, id_tipo: int) -> None:
    """Regista a consulta no histórico e exibe o custo descontado."""
    # Pede uma instância de ligação.
    conn = conectar()
    # Se a instância for inválida, termina.
    if not conn:
        return
        
    try:
        cursor = conn.cursor()
        # Gera uma string de texto com a data e hora atuais do relógio do sistema, formatada como "Ano-Mês-Dia Hora:Minuto:Segundo".
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insere o registo da consulta
        # Adiciona uma nova entrada no histórico de faturação, associando quem fez o pedido ('id_utilizador'), qual o tipo de pedido ('id_tipo') e a que horas ('data_hora').
        cursor.execute("INSERT INTO consulta (id_utilizador, id_tipo, data_hora) VALUES (?, ?, ?)", 
                      (id_utilizador, id_tipo, data_hora))
                      
        # Vai buscar os dados para mostrar ao utilizador
        # Faz uma leitura de volta à base de dados para ir buscar o texto legível da consulta e o seu preço monetário exato associado àquele 'id_tipo'.
        cursor.execute("SELECT descricao, custo FROM tipo_consulta WHERE id_tipo = ?", (id_tipo,))
        # Extrai essa linha (tuplo).
        tipo = cursor.fetchone()
        
        # Confirma a transação da inserção inicial da fatura, gravando-a permanentemente.
        conn.commit()
        
        # Se conseguiu obter os dados descritivos da consulta efetuada.
        if tipo: 
            # Imprime uma notificação em formato de recibo financeiro usando 'f-strings'. Formata o número float do preço para ter sempre 2 casas decimais ('.2f') seguidas do símbolo do Euro.
            print(f"\n[SISTEMA FINANCEIRO] Cobrança: '{tipo[0]}' | Valor descontado: {tipo[1]:.2f}€")
            
    except Exception as e: 
        # Em caso de erro na cobrança ou registo, aciona este print de aviso.
        print(f"Erro ao processar cobrança: {e}")
    finally: 
        # Encerra impreterivelmente a conexão.
        conn.close()


# --- CONSULTAS SQL EXISTENTES ---

def listar_equipas(id_utilizador: int) -> None:
    conn = conectar()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        # Faz um pedido SQL elementar para extrair a lista de nomes e cidades de todos os clubes.
        cursor.execute("SELECT nome, cidade FROM equipa")
        # Recolhe todas as equipas em memória.
        resultados = cursor.fetchall()
        
        print("\n---LISTA DE EQUIPAS ---")
        # Se a lista vier sem elementos.
        if not resultados:
            print("Não há equipas registadas.")
        # Caso existam equipas.
        else:
            # Percorre iterativamente cada equipa devolvida.
            for e in resultados: 
                # Usa um operador ternário: se a cidade (índice 1) existir e não for nula, assume o seu nome. Se for nula, assume a string 'N/D' (Não Disponível).
                cidade = e[1] if e[1] else 'N/D'
                # Imprime o nome da equipa (índice 0) e a cidade entre parênteses.
                print(f"{e[0]} ({cidade})")
                
        # Independentemente do resultado na listagem, chama a função financeira para faturar esta consulta usando o 'id_tipo' 1.
        registar_cobrar_consulta(id_utilizador, 1)
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
    finally:
        conn.close()


def jogadores_mais_5_golos(id_utilizador: int) -> None:
    conn = conectar()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        # Lógica SQL Avançada:
        # Cruza as tabelas 'jogador', 'golo' e 'equipa'. 
        # Usa 'GROUP BY' para agregar os golos por jogador e a cláusula 'HAVING total > 5' atua como um filtro pós-agregação (só aceita quem soma mais de 5 remates certeiros). 
        # Ordena de forma decrescente ('DESC') pelo volume total de golos.
        cursor.execute("""
            SELECT j.nome, e.nome, COUNT(g.id_golo) as total FROM jogador j
            JOIN golo g ON j.id_jogador = g.id_jogador 
            JOIN equipa e ON j.id_equipa = e.id_equipa
            GROUP BY j.id_jogador 
            HAVING total > 5 
            ORDER BY total DESC
        """)
        resultados = cursor.fetchall()
        
        print("\n--- JOGADORES COM MAIS DE 5 GOLOS ---")
        if not resultados:
            print("Nenhum jogador atingiu esta marca ainda.")
        else:
            for p in resultados: 
                # p[0] é o jogador, p[1] é a equipa e p[2] é a contagem de golos.
                print(f"{p[0]} ({p[1]}) - {p[2]} Golos")
                
        # Cobra o preço associado à consulta de ID número 2.
        registar_cobrar_consulta(id_utilizador, 2)
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
    finally:
        conn.close()


def top_5_artilheiros(id_utilizador: int) -> None:
    conn = conectar()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        # Lógica SQL Avançada (Window Functions & Subqueries):
        # A subconsulta interior (dentro dos parênteses) conta os golos e usa 'RANK() OVER()' para atribuir uma posição matemática no pódio a cada jogador.
        # A consulta exterior (SELECT *) filtra apenas os jogadores cuja posição (ranking) seja menor ou igual a 5.
        cursor.execute("""
            SELECT * FROM (
                SELECT j.nome, e.nome as equipa, COUNT(g.id_golo) as total, RANK() OVER(ORDER BY COUNT(g.id_golo) DESC) as ranking
                FROM jogador j 
                JOIN golo g ON j.id_jogador = g.id_jogador 
                JOIN equipa e ON j.id_equipa = e.id_equipa
                GROUP BY j.id_jogador
            ) WHERE ranking <= 5
        """)
        resultados = cursor.fetchall()
        
        print("\n---TOP 5 ARTILHEIROS---")
        if not resultados:
            print("Ainda não há golos suficientes para formar o ranking.")
        else:
            for p in resultados: 
                # p[3] traz o lugar no ranking alcançado pelo artilheiro.
                print(f"#{p[3]} | {p[0]} ({p[1]}) - {p[2]} Golos")
                
        # Emite a fatura referente à consulta com ID 3.
        registar_cobrar_consulta(id_utilizador, 3)
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
    finally:
        conn.close()


def equipas_invictas(id_utilizador: int) -> None:
    conn = conectar()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        # Lógica SQL Avançada (NOT IN & UNION):
        # Vai procurar todas as equipas cujo identificador numérico (ID) NÃO ESTEJA ('NOT IN') na lista gerada em baixo.
        # A subconsulta 'UNION' junta duas listas numa só: A lista dos que perderam a jogar em casa E a lista dos que perderam a jogar fora.
        # Conclusão: Quem não faz parte da lista dos perdedores, é porque está invicto.
        cursor.execute("""
            SELECT nome FROM equipa WHERE id_equipa NOT IN (
                SELECT id_equipa_casa FROM jogo WHERE golos_casa < golos_fora 
                UNION 
                SELECT id_equipa_fora FROM jogo WHERE golos_fora < golos_casa
            )
        """)
        resultados = cursor.fetchall()
        
        print("\n---EQUIPAS INVICTAS---")
        if not resultados:
            # Caso a lista submetida pelo SQL esteja vazia, significa que a subconsulta provou que todos já perderam.
            print("Nenhuma equipa está invicta. Todas já perderam jogos.")
        else:
            for e in resultados: 
                print(f"{e[0]}")
                
        # Registar custo sob o produto com o ID de catálogo 4.
        registar_cobrar_consulta(id_utilizador, 4)
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
    finally:
        conn.close()


# --- NOVAS CONSULTAS ADICIONADAS ---

def pesquisa_curinga(id_utilizador: int) -> None:
    """Dado um nome curinga, mostra dados do jogador e a sua equipa."""
    # Solicita um bocado de texto (letras ou sílabas soltas) para fazer a procura. Limpa margens brancas.
    nome_pesquisa = input("\nDigita parte do nome do jogador a pesquisar: ").strip()
    # Se o utilizador só carregou 'Enter', desiste para não pesquisar nomes vazios.
    if not nome_pesquisa:
        print("Operação cancelada.")
        return
        
    conn = conectar()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        # Lógica SQL Avançada (Cláusula LIKE e Wildcards '%'):
        # Procura o jogador pelo nome, desde que o nome da base de dados contenha a palavra inserida algures no meio (indicado pelas percentagens % antes e depois do parâmetro).
        cursor.execute("""
            SELECT j.nome, j.posicao, e.nome FROM jogador j 
            JOIN equipa e ON j.id_equipa = e.id_equipa 
            WHERE j.nome LIKE ?
        """, (f"%{nome_pesquisa}%",))
        resultados = cursor.fetchall()
        
        print("\n---RESULTADOS DA PESQUISA ---")
        if not resultados: 
            print("Nenhum jogador encontrado com esse nome.")
        else:
            for r in resultados: 
                print(f"{r[0]} | Posição: {r[1]} | Equipa: {r[2]}")
                
        # Debita a consulta número 5 na conta do utilizador.
        registar_cobrar_consulta(id_utilizador, 5)
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
    finally:
        conn.close()


def jogadores_acima_media(id_utilizador: int) -> None:
    """Lista jogadores com mais golos que a média da liga."""
    conn = conectar()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        # Lógica SQL Avançada (Subquery Escalar e CAST):
        # Compara a soma agrupada dos golos individuais contra um limite dinâmico. Esse limite é calculado através de uma divisão matemática em tempo real: O total geral de golos convertido em número flutuante (CAST AS FLOAT) dividido pelo total de jogadores diferentes que já marcaram alguma vez (COUNT DISTINCT id_jogador).
        cursor.execute("""
            SELECT j.nome, e.nome, COUNT(g.id_golo) as total FROM jogador j
            JOIN equipa e ON j.id_equipa = e.id_equipa
            JOIN golo g ON j.id_jogador = g.id_jogador
            GROUP BY j.id_jogador
            HAVING total > (SELECT CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT id_jogador) FROM golo)
            ORDER BY total DESC
        """)
        resultados = cursor.fetchall()
        
        print("\n---JOGADORES ACIMA DA MÉDIA DE GOLOS ---")
        if not resultados:
            print("Não há dados suficientes para calcular a média.")
        else:
            for p in resultados: 
                print(f"{p[0]} ({p[1]}) - {p[2]} Golos")
                
        # Imputa a cobrança do produto com ID 6.
        registar_cobrar_consulta(id_utilizador, 6)
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
    finally:
        conn.close()


def jogos_acima_media_golos(id_utilizador: int) -> None:
    """Lista partidas cuja soma de golos foi maior que a média."""
    conn = conectar()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        # Lógica SQL Avançada (Somatórios Horizontais e Verticais Combinados):
        # Calcula um campo falso chamado 'total_jogo' ao somar a linha de golos da casa e de fora horizontalmente. A seguir, na cláusula WHERE, compara esse 'total_jogo' com a média global estrita de todos os jogos efetivamente disputados (que não têm resultados nulos).
        cursor.execute("""
            SELECT e1.nome, e2.nome, j.golos_casa, j.golos_fora, (j.golos_casa + j.golos_fora) as total_jogo
            FROM jogo j
            JOIN equipa e1 ON j.id_equipa_casa = e1.id_equipa
            JOIN equipa e2 ON j.id_equipa_fora = e2.id_equipa
            WHERE total_jogo > (SELECT CAST(SUM(golos_casa + golos_fora) AS FLOAT) / COUNT(id_jogo) FROM jogo WHERE golos_casa IS NOT NULL)
            ORDER BY total_jogo DESC
        """)
        resultados = cursor.fetchall()
        
        print("\n---JOGOS COM GOLOS ACIMA DA MÉDIA ---")
        if not resultados:
            print("Não há jogos suficientes para calcular esta métrica.")
        else:
            for j in resultados: 
                # Imprime quem jogou contra quem e com a amostra em formato estético de Placard. O índice [4] é o total individual desse jogo.
                print(f"{j[0]} {j[2]}-{j[3]} {j[1]} (Total: {j[4]} golos)")
                
        # Transação de pagamento para a 7ª opção do catálogo.
        registar_cobrar_consulta(id_utilizador, 7)
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
    finally:
        conn.close()


def ver_minha_conta(id_utilizador: int, conta_utilizador: str) -> None:
    conn = conectar()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        # Lógica SQL Avançada (Running Total / Soma Progressiva):
        # Lê o histórico do cliente da tabela 'consulta'.
        # O uso do 'SUM(t.custo) OVER (ORDER BY c.data_hora)' atua como um extrato bancário, acumulando a fatura financeiramente de cima a baixo ao longo do tempo.
        cursor.execute("""
            SELECT c.data_hora, t.descricao, t.custo, SUM(t.custo) OVER (ORDER BY c.data_hora) as acumulado
            FROM consulta c 
            JOIN tipo_consulta t ON c.id_tipo = t.id_tipo
            WHERE c.id_utilizador = ? 
            ORDER BY c.data_hora
        """, (id_utilizador,))
        resultados = cursor.fetchall()
        
        # Cabeçalho decorativo exclusivo com as letras do cliente em maiúsculas ('.upper()').
        print("\n" + "="*80)
        print(f"   A TUA CONTA: HISTÓRICO E DÍVIDA ({conta_utilizador.upper()})")
        print("="*80)
        
        # Se a tabela ainda estiver em branco.
        if not resultados: 
            print("Ainda não realizaste consultas pagas. A tua conta está a zeros!")
        else:
            # Imprime os cabeçalhos em grelha tabular bem alinhados à esquerda (uso de '<').
            print(f"{'DATA/HORA':<20} | {'DESCRIÇÃO':<35} | {'CUSTO':<6} | {'DÍVIDA TOTAL'}")
            print("-" * 80)
            for linha in resultados: 
                # Exibe linha a linha. Corta a descrição em 33 letras ('[:33]') para não quebrar a grelha por excesso de palavras. Os valores pecuniários usam 2 casas decimais.
                print(f"{linha[0]:<20} | {linha[1][:33]:<35} | {linha[2]:>5.2f}€ | {linha[3]:>9.2f}€")
                
    except Exception as e:
        print(f"Erro ao carregar os dados da conta: {e}")
    finally:
        conn.close()


def arrancar_menu_user(conta_utilizador: str) -> None:
    # A primeira coisa que o menu faz ao iniciar é certificar-se silenciosamente de que os preços e descrições existem na base de dados (se for o primeiro arranque do programa no computador).
    garantir_tipos_consulta()
    # Identifica o utilizador que abriu a janela, traduzindo o nome de utilizador introduzido para o seu número de identificação exato para cruzar as finanças mais tarde.
    id_user = obter_id_utilizador(conta_utilizador)
    
    # Previne que o sistema avance se houver um erro grave na extração do ID
    # Se por algum motivo o ID vier a nulo (Ex: Ficheiro SQLite indisponível neste instante).
    if not id_user:
        print("\nErro Crítico: Não foi possível carregar o teu perfil. Contacta o administrador.")
        return # Trava a execução do painel imediatamente.
    
    # Ciclo perpétuo para renderização do painel interativo.
    while True:
        # Desenho textual na consola demonstrando os preços da tabela original e saudações personalizadas.
        print("\n" + "="*55)
        print(f"   MENU DE CONSULTAS | Bem-vindo, {conta_utilizador}")
        print("="*55)
        print("1. Listar todas as equipas [1.00€]")
        print("2. Jogadores com mais de 5 golos [1.50€]")
        print("3. Top 5 Artilheiros da Liga [2.50€]")
        print("4. Equipas Invictas [3.00€]")
        print("5. Pesquisar Jogador (Curinga) [1.00€]")
        print("6. Jogadores Acima da Média de Golos [3.50€]")
        print("7. Jogos com Golos Acima da Média [3.50€]")
        print("\n--- GESTÃO DE CONTA ---")
        print("8. Ver o meu histórico e custo acumulado")
        print("9. Logout")
        
        # O utilizador techa um número que é posteriormente limpo de espaços ocultos de ponta a ponta.
        escolha = input("Escolhe uma opção: ").strip()
        
        # Sequência lógica de decisão. Cada número aciona um ramo diferente das opções de jogo associadas à base de dados.
        if escolha == '1': listar_equipas(id_user)
        elif escolha == '2': jogadores_mais_5_golos(id_user)
        elif escolha == '3': top_5_artilheiros(id_user)
        elif escolha == '4': equipas_invictas(id_user)
        elif escolha == '5': pesquisa_curinga(id_user)
        elif escolha == '6': jogadores_acima_media(id_user)
        elif escolha == '7': jogos_acima_media_golos(id_user)
        # Se clicar '8', salta para a função exclusiva do perfil e contas a acertar.
        elif escolha == '8': ver_minha_conta(id_user, conta_utilizador)
        # Se for o '9', destrói a roda deste menu iterativo devolvendo o controlo ao espaço log-in/ecrã anterior.
        elif escolha == '9': 
            print(f"\nSessão terminada. Obrigado pela preferência, {conta_utilizador}!")
            break
        # Bloqueador de erros por utilização imprópria da caixa de texto (como escrever letras no menu principal).
        else: 
            print("Opção inválida! Escolhe um número de 1 a 9.")