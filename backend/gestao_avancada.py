# Importa a função 'conectar' do módulo local 'backend.database' para permitir o estabelecimento da ligação à base de dados SQLite.
from backend.database import conectar
# Importa a função 'registar_log' do módulo 'backend.gerir_utilizadores' para auditar e guardar o registo textual de ações importantes.
from backend.gerir_utilizadores import registar_log

def listar_equipas() -> None:
    # Inicia a ligação à base de dados.
    conn = conectar()
    # Se a ligação falhar (devolver nulo/falso), a função termina imediatamente sem tentar executar o resto.
    if not conn: return
    try:
        # Cria um objeto 'cursor' nativo do SQLite para executar e transportar comandos SQL.
        cursor = conn.cursor()
        # Executa a consulta SQL para obter o ID, o nome e a cidade de todas as equipas guardadas na tabela 'equipa', ordenadas alfabeticamente pelo nome.
        cursor.execute("SELECT id_equipa, nome, cidade FROM equipa ORDER BY nome")
        # Extrai todas as linhas resultantes da consulta e guarda-as na variável 'equipas' (normalmente uma lista de tuplos).
        equipas = cursor.fetchall()
        # Imprime o título e o cabeçalho no ecrã (consola).
        print("\n---LISTA DE EQUIPAS ---")
        # Percorre sequencialmente cada tuplo da lista de resultados, desempacotando os 3 valores em variáveis locais.
        for id_eq, nome, cidade in equipas:
            # Imprime os dados da equipa formatados em grelha. Os símbolos '<3' e '<20' forçam o alinhamento à esquerda. Se a variável cidade for nula (None), usa o operador lógico 'or' para mostrar 'N/D' (Não Disponível).
            print(f"ID: {id_eq:<3} | Nome: {nome:<20} | Cidade: {cidade or 'N/D'}")
        # Desenha uma linha tracejada horizontal para finalizar a tabela no ecrã.
        print("-" * 40)
    except Exception as e:
        # Caso ocorra alguma falha na leitura ou comunicação de dados, apanha o erro e mostra a sua origem técnica.
        print(f"Erro ao listar equipas: {e}")
    finally:
        # Bloco incondicional de fecho, garantindo que a ligação é terminada para não bloquear recursos em memória do computador.
        conn.close()

def adicionar_equipa() -> None:
    # Mostra qual a operação atual.
    print("\n-- ADICIONAR NOVA EQUIPA --")
    # Pede o nome da equipa através do teclado e usa '.strip()' para limpar possíveis espaços inseridos por lapso no início ou no fim do texto.
    nome = input("Nome da Equipa: ").strip()
    # Valida se o utilizador pressionou 'Enter' sem digitar nada.
    if not nome:
        print("Erro: O nome da equipa é obrigatório!")
        return # Cancela o registo por insuficiência de dados.
        
    # Pede a cidade representativa da equipa.
    cidade = input("Cidade (opcional): ").strip()
    # Atribui o valor do texto recolhido caso exista, se o texto estiver vazio (''), força a variável a adotar o valor especial nulo do Python (None).
    cidade = cidade if cidade else None

    # Efetua nova ligação à base de dados para proceder à escrita.
    conn = conectar()
    if not conn: return
    try:
        cursor = conn.cursor()
        # Prepara a instrução SQL de inserção (INSERT INTO). As interrogações ('?') inserem as variáveis de forma parametrizada, o que bloqueia perigosos ataques de Injeção SQL.
        cursor.execute("INSERT INTO equipa (nome, cidade) VALUES (?, ?)", (nome, cidade))
        # O 'commit' fecha a transação, gravando o novo registo permanentemente no disco.
        conn.commit()
        print(f"Sucesso: Equipa '{nome}' registada!")
        # Aciona o sistema de log (ficheiro de texto local) apontando que uma inserção ocorreu com aquele nome específico.
        registar_log("auditoria_jogos.log", "INSERÇÃO", f"Equipa '{nome}' adicionada ao sistema.")
    except Exception as e:
        # Lida de forma graciosa com erros da base de dados (ex: restrição única/duplicação se houver).
        print(f"Erro ao adicionar equipa: {e}")
    finally:
        # Encerramento preventivo da porta de comunicação SQLite.
        conn.close()

def listar_jogadores() -> None:
    conn = conectar()
    if not conn: return
    try:
        cursor = conn.cursor()
        # Instrução de pesquisa que cruza duas tabelas (jogador e equipa) usando um 'JOIN'.
        # Isto permite substituir o número do ID da equipa (id_equipa) pela sua designação em formato de texto (e.nome) para ser legível aos humanos, ordenando primeiro pelo nome da equipa e a seguir pelo do jogador.
        cursor.execute("""
            SELECT j.id_jogador, j.nome, j.posicao, e.nome 
            FROM jogador j
            JOIN equipa e ON j.id_equipa = e.id_equipa
            ORDER BY e.nome, j.nome
        """)
        # Extrai toda a lista de resultados combinados.
        jogadores = cursor.fetchall()
        print("\n--- LISTA DE JOGADORES ---")
        # Inicia o ciclo que distribui as 4 colunas solicitadas nas variáveis de controlo.
        for id_jog, nome, posicao, equipa in jogadores:
            # Mostra a linha em formato de 'f-string' de tamanho controlado (para parecer uma tabela em terminal).
            print(f"ID: {id_jog:<3} | {nome:<20} | Pos: {posicao:<10} | Equipa: {equipa}")
        print("-" * 55)
    except Exception as e:
        # Tratamento de exceções não previstas.
        print(f"Erro ao listar jogadores: {e}")
    finally:
        # Purga de ligação inativa.
        conn.close()

def adicionar_jogador() -> None:
    print("\n-- ADICIONAR NOVO JOGADOR --")
    # Pede dados obrigatórios do atleta.
    nome = input("Nome do Jogador: ").strip()
    posicao = input("Posição (Ex: Avançado, Defesa): ").strip()
    
    # Avalia se quer o nome quer a posição estão vazios. Se um deles estiver, a condição é ativada.
    if not nome or not posicao:
        print("Erro: O nome e a posição são obrigatórios!")
        return
        
    # Executa a função previamente definida para imprimir no ecrã a lista das equipas, facilitando a escolha da equipa certa pelo administrador.
    listar_equipas()
    # Solicita qual o identificador numérico da equipa.
    id_equipa = input("\nID da Equipa a que o jogador pertence: ").strip()
    
    conn = conectar()
    if not conn: return
    try:
        # Converte a resposta em texto do teclado (ex: "5") num autêntico número inteiro matemático (5).
        id_eq_int = int(id_equipa)
        cursor = conn.cursor()
        
        # Verifica se a equipa existe
        # Interroga a base de dados em busca da equipa com aquele ID em específico.
        cursor.execute("SELECT nome FROM equipa WHERE id_equipa = ?", (id_eq_int,))
        # O '.fetchone()' tenta capturar um resultado. Se for falso ('not'), deduz-se que o utilizador escolheu uma equipa que não existe.
        if not cursor.fetchone():
            print("Erro: ID de equipa inválido.")
            return # Interrupção forçada.
            
        # Tendo os dados validados, submete a instrução de inserção na tabela de jogadores.
        cursor.execute("INSERT INTO jogador (nome, posicao, id_equipa) VALUES (?, ?, ?)", (nome, posicao, id_eq_int))
        conn.commit() # Validação da transação de escrita.
        print(f"Sucesso: Jogador '{nome}' registado!")
        # Auditoria da adição.
        registar_log("auditoria_jogos.log", "INSERÇÃO", f"Jogador '{nome}' associado à equipa ID {id_eq_int}.")
    except ValueError:
        # Interceção direcionada: se a conversão 'int(id_equipa)' falhar devido ao utilizador escrever letras em vez de um número, salta para aqui e evita parar o programa por quebra crítica (crash).
        print("Erro: O ID da equipa tem de ser um número inteiro!")
    except Exception as e:
        # Interceção genérica para falhas de motor de dados.
        print(f"Erro ao adicionar jogador: {e}")
    finally:
        # Limpeza sistemática do canal SQLite.
        conn.close()

def registar_golo() -> None:
    print("\n-- REGISTAR NOVO GOLO --")
    
    # Importar aqui para evitar "circular imports"
    # Devido à natureza bidirecional da dependência entre estes ficheiros lógicos, atrasamos e realizamos a importação apenas dentro da função e quando necessária, de forma a impedir que o Python bloqueie por se tentar auto-referenciar repetidamente no topo do script.
    from backend.gerir_jogos import listar_jogos 
    listar_jogos() # Mostra o calendário para o utilizador consultar os IDs dos jogos passados.
    
    # Lê a escolha do jogo no qual ocorreu o golo.
    id_jogo = input("\nID do Jogo onde o golo ocorreu (ou 0 para cancelar): ").strip()
    # Mecanismo fácil de saída precoce, usando o '0' ou tecla 'Enter' vazia.
    if id_jogo == '0' or not id_jogo: return
    
    # Mostra a lista de todos os atletas como ajuda visual.
    listar_jogadores()
    id_jogador = input("\nID do Jogador que marcou: ").strip()
    minuto = input("Minuto do golo (1-130): ").strip()
    
    conn = conectar()
    if not conn: return
    try:
        # Processo de casting (conversão forçada de tipo) das variáveis que estão em formato string de texto para inteiros numéricos.
        id_jg_int = int(id_jogo)
        id_jog_int = int(id_jogador)
        minuto_int = int(minuto)
        
        # Lógica de proteção de domínio desportivo: nenhum golo ocorre antes do início do jogo nem depois de um prolongamento genérico expectável de 130 minutos.
        if minuto_int < 1 or minuto_int > 130:
            print("Erro: Minuto inválido.")
            return
            
        cursor = conn.cursor()
        # Escreve o registo cruzando chaves estrangeiras ('id_jogo' e 'id_jogador') para criar a ligação entre o jogo, o desportista e a sua métrica (minuto do golo).
        cursor.execute("INSERT INTO golo (id_jogo, id_jogador, minuto) VALUES (?, ?, ?)", (id_jg_int, id_jog_int, minuto_int))
        conn.commit() # Salvaguarda das alterações efetuadas acima.
        print(f"Sucesso: Golo registado ao minuto {minuto_int}!")
        # Gravação desta estatística para efeitos de segurança e auditoria retroativa.
        registar_log("auditoria_jogos.log", "INSERÇÃO", f"Golo registado (Jogo: {id_jg_int}, Jogador: {id_jog_int}, Minuto: {minuto_int}).")
    except ValueError:
        # Se qualquer um dos valores requeridos sofrer falha de conversão numérica devido a digitação equivocada (ex: um ID ou um minuto com letras introduzidas).
        print("Erro: Os IDs e o minuto têm de ser números inteiros!")
    except Exception as e:
        # Informa caso os IDs submetidos falhem as regras de dependência impostas pela base de dados (Ex: Tentar associar o golo a um jogo que afinal não existe).
        print(f"Erro ao registar golo (verifica se os IDs de jogo e jogador existem): {e}")
    finally:
        # Fecha a torneira de dados para estabilidade de memória operacional.
        conn.close()


def menu_gestao_avancada() -> None:
    """Sub-menu para a Gestão de Equipas, Jogadores e Golos."""
    # Estrutura em "loop" inquebrável por defeito, servindo para desenhar a interface repetidamente.
    while True:
        # Corpo visual do painel de opções desportivas avançadas.
        print("\n=== GESTÃO AVANÇADA ===")
        print("1. Listar Equipas")
        print("2. Adicionar Equipa")
        print("3. Listar Jogadores")
        print("4. Adicionar Jogador")
        print("5. Registar Golo Individual")
        print("6. Voltar ao Painel Geral")
        
        # Pede que o administrador eleja e introduza o seu número preferencial.
        escolha = input("Opção: ").strip()
        
        # Estrutura "switch-case" convertida para "if-elif" em Python. Relaciona a seleção com a função correspondente desenhada em cima.
        if escolha == '1': listar_equipas()
        elif escolha == '2': adicionar_equipa()
        elif escolha == '3': listar_jogadores()
        elif escolha == '4': adicionar_jogador()
        elif escolha == '5': registar_golo()
        # Ao premir '6', a palavra reservada 'break' rasga o ciclo repetitivo e termina esta função, causando a retoma ao menu anterior de onde este foi invocado.
        elif escolha == '6': break
        # Se a opção cair fora da escala mapeada ou incluir caracteres espúrios, cai neste 'else' alertando do erro.
        else: print("Opção inválida!")