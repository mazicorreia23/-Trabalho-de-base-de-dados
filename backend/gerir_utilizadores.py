import os # Importa o módulo 'os', que permite interagir com o sistema operativo (criar pastas, manipular caminhos de ficheiros, etc.).
from datetime import datetime # Importa o objeto 'datetime' para podermos capturar e formatar a data e hora atuais do sistema.
from backend.database import conectar # Importa a função 'conectar' do nosso ficheiro 'database' para estabelecer a ligação à base de dados SQLite.
from backend.auth import encriptar_senha # Importa a função que transforma a palavra-passe em texto limpo num hash seguro irreversível.

# --- CONSTANTES ---
# Centralizamos os nomes das pastas e ficheiros para ser mais fácil alterar no futuro sem ter de procurar pelo código todo.
PASTA_LOGS = "logs" # Nome da diretoria onde os ficheiros de registo (logs) serão guardados.
FICHEIRO_LOG_USERS = "auditoria_utilizadores.log" # Nome do ficheiro de texto onde ficam registadas as ações dos administradores.


def registar_log(nome_ficheiro: str, acao: str, detalhes: str) -> None:
    """Escreve a ação num ficheiro de log dinâmico dentro da pasta 'logs'."""
    # Garante que a pasta definida na constante 'PASTA_LOGS' existe. O 'exist_ok=True' evita que o programa dê erro se a pasta já lá estiver.
    os.makedirs(PASTA_LOGS, exist_ok=True)
    # Constrói o caminho seguro para o ficheiro juntando a pasta e o nome do ficheiro (ex: 'logs/auditoria_utilizadores.log').
    caminho_completo = os.path.join(PASTA_LOGS, nome_ficheiro)
    
    # Captura o momento exato da ação e converte-o para uma string de texto legível no formato "Ano-Mês-Dia Hora:Minuto:Segundo".
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Constrói a mensagem final que será escrita na linha do ficheiro, juntando a data, o tipo de ação e o detalhe do que aconteceu.
    mensagem = f"[{data_hora}] AÇÃO: {acao} | DETALHES: {detalhes}\n"
    
    # Bloco 'try' para proteger o programa caso haja problemas de permissões ao tentar escrever no disco.
    try:
        # Abre o ficheiro em modo "a" (append), o que significa que vai adicionar a nova mensagem no final do ficheiro sem apagar o que lá estava. Usa codificação UTF-8 para suportar acentos.
        with open(caminho_completo, "a", encoding="utf-8") as ficheiro:
            ficheiro.write(mensagem) # Escreve a linha preparada na variável 'mensagem' dentro do ficheiro de texto.
    except Exception as e:
        # Se falhar, avisa o utilizador no ecrã em vez de interromper o programa de forma abrupta.
        print(f"[Aviso] Não foi possível escrever no log: {e}")


def ver_logs_no_terminal() -> None:
    """Lê o ficheiro de log de utilizadores e mostra-o no terminal."""
    # Junta a constante da pasta com a do ficheiro de utilizadores para saber exatamente onde ler os dados.
    arquivo_log = os.path.join(PASTA_LOGS, FICHEIRO_LOG_USERS)
    
    # Imprime um cabeçalho estético no ecrã (consola) com 70 sinais de igual.
    print("\n" + "="*70)
    print("HISTÓRICO DE AUDITORIA (UTILIZADORES)")
    print("="*70)
    
    # Tenta abrir e ler o ficheiro, protegendo contra possíveis erros de leitura.
    try:
        # Primeiro, verifica se o ficheiro efetivamente existe no disco para não dar erro ao tentar abrir um ficheiro fantasma.
        if os.path.exists(arquivo_log):
            # Abre o ficheiro em modo "r" (read - leitura). O 'with' garante que o ficheiro é fechado automaticamente no fim.
            with open(arquivo_log, "r", encoding="utf-8") as ficheiro:
                conteudo = ficheiro.read() # Lê todo o texto do ficheiro para a variável 'conteudo'.
                # Verifica se o ficheiro tem texto lá dentro (o .strip() remove espaços vazios ou quebras de linha a mais).
                if conteudo.strip():
                    print(conteudo.strip()) # Imprime o conteúdo do log no ecrã.
                else:
                    # Se o ficheiro existir mas estiver vazio por dentro.
                    print("O ficheiro de log está vazio.")
        else:
            # Se o comando 'os.path.exists' devolver Falso, significa que a pasta ou o ficheiro ainda não foram criados.
            print("Ainda não existem registos de log de utilizadores.")
    except Exception as e:
        # Captura e imprime problemas inesperados (ex: ficheiro corrompido).
        print(f"Erro ao ler os logs: {e}")
    finally:
        # Imprime o rodapé independentemente do sucesso ou falha da leitura.
        print("="*70)


def listar_utilizadores() -> bool:
    """
    Mostra todos os utilizadores (exceto o admin).
    Retorna True se existirem utilizadores, False caso contrário.
    """
    conn = conectar() # Inicia a ligação com a base de dados SQLite.
    if not conn: # Aborta se a ligação falhar.
        return False
        
    try:
        cursor = conn.cursor() # Cria o cursor para executar comandos SQL.
        # Executa uma instrução 'SELECT' para ir buscar o ID e a Conta, mas exclui (!=) o administrador. Ordena pelo ID.
        cursor.execute("SELECT id_utilizador, conta FROM utilizador WHERE conta != 'admin' ORDER BY id_utilizador")
        utilizadores = cursor.fetchall() # Extrai todos os resultados encontrados e guarda-os numa lista de tuplos.
        
        print("\n--- LISTA DE UTILIZADORES ---")
        # Se a lista vier vazia, avisa o sistema e devolve 'Falso'.
        if not utilizadores:
            print("Não existem utilizadores registados.")
            return False
            
        # Percorre a lista desempacotando o tuplo em 'id_user' e 'conta'.
        for id_user, conta in utilizadores:
            # Imprime os dados. O '<3' formata o ID para ocupar sempre 3 espaços à esquerda, mantendo tudo alinhado.
            print(f"ID: {id_user:<3} | Conta: {conta}")
        print("-" * 29) # Linha de separação estética.
        return True # Devolve Verdadeiro porque encontrou e listou utilizadores.
        
    except Exception as e:
        # Interceta quebras no processo de base de dados.
        print(f"Erro ao listar utilizadores: {e}")
        return False
    finally:
        # Fecha sempre a ligação à base de dados para libertar a memória.
        conn.close()


def adicionar_utilizador() -> None:
    """Administrador adiciona um utilizador e regista no LOG."""
    print("\n-- ADICIONAR UTILIZADOR --")
    # Pede o nome de conta ao administrador e usa .strip() para remover espaços acidentais nas pontas.
    conta = input("Nova conta: ").strip()
    
    # Se o administrador deu apenas 'Enter' sem escrever nada.
    if not conta:
        print("Erro: O nome da conta não pode estar vazio.")
        return
        
    # Converte o que foi escrito para minúsculas e verifica se está a tentar criar outro 'admin'.
    if conta.lower() == 'admin':
        print("Erro: Não podes duplicar a conta de Administrador.")
        return

    # Pede a palavra-passe e remove espaços externos.
    senha = input("Palavra-passe: ").strip()
    # Bloqueia palavras-passe em branco.
    if not senha:
        print("Erro: A palavra-passe não pode estar vazia.")
        return

    conn = conectar() # Liga à base de dados.
    if not conn:
        return
        
    try:
        cursor = conn.cursor()
        # Passa a palavra-passe legível pela função que a transforma num 'Hash' seguro (ex: SHA-256) antes de gravar.
        senha_hash = encriptar_senha(senha)
        
        # Verifica se já existe um utilizador com esse nome na tabela. Usa o LOWER() para que "Joao" e "joao" sejam vistos como iguais.
        cursor.execute("SELECT id_utilizador FROM utilizador WHERE LOWER(conta) = ?", (conta.lower(),))
        if cursor.fetchone(): # Se encontrou alguma linha, é porque o nome já está em uso.
            print("Erro: Esta conta já existe no sistema.")
            return # Cancela o registo.
            
        # Prepara a instrução para inserir os novos dados na tabela 'utilizador'.
        cursor.execute("INSERT INTO utilizador (conta, palavra_passe) VALUES (?, ?)", (conta, senha_hash))
        conn.commit() # Guarda as alterações fisicamente no ficheiro da base de dados.
        print(f"Sucesso: Utilizador '{conta}' criado!")
        
        # Chama a função de registo para gravar a auditoria dizendo quem foi adicionado.
        registar_log(FICHEIRO_LOG_USERS, "INSERÇÃO", f"Conta '{conta}' criada.")
        
    except Exception as e:
        print(f"Erro ao inserir utilizador: {e}")
    finally:
        conn.close()


def editar_utilizador() -> None:
    """Administrador altera a palavra-passe de um utilizador e regista no LOG."""
    # Primeiro chama a função que lista os utilizadores. Se devolver False (não há ninguém), aborta imediatamente.
    if not listar_utilizadores():
        return
        
    # Pede ao administrador o número de ID do utilizador a editar.
    id_editar = input("\nDigita o ID do utilizador a editar (ou 0 para cancelar): ").strip()
    # Se o admin digitou '0' ou deixou em branco, a função para por aqui.
    if id_editar == '0' or not id_editar:
        return
        
    conn = conectar()
    if not conn:
        return
        
    try:
        cursor = conn.cursor()
        # Tenta procurar o utilizador pelo ID inserido, garantindo por segurança extra que esse ID não pertence ao 'admin'.
        cursor.execute("SELECT conta FROM utilizador WHERE id_utilizador = ? AND conta != 'admin'", (id_editar,))
        resultado = cursor.fetchone() # Traz o primeiro resultado que cruzar.
        
        if not resultado: # Se não trouxe nada, o ID não existe ou o admin tentou alterar as suas próprias credenciais por aqui.
            print("Erro: ID inválido ou tentativa de alterar o Administrador.")
            return
            
        # Extrai o nome da conta que estava dentro do tuplo devolvido pela base de dados.
        nome_conta = resultado[0]
        # Pede a nova senha, mostrando no texto de pedido o nome do utilizador alvo.
        nova_senha = input(f"Digita a nova palavra-passe para '{nome_conta}': ").strip()
        
        # Bloqueia a alteração se a nova senha estiver em branco.
        if not nova_senha:
            print("Erro: A palavra-passe não pode estar vazia.")
            return
            
        # Encripta a nova palavra-passe.
        senha_hash = encriptar_senha(nova_senha)
        
        # Executa o comando UPDATE (Atualizar) alterando apenas o campo 'palavra_passe' na linha correspondente a este ID.
        cursor.execute("UPDATE utilizador SET palavra_passe = ? WHERE id_utilizador = ?", (senha_hash, id_editar))
        conn.commit() # Consolida a modificação.
        print(f"Sucesso: Palavra-passe de '{nome_conta}' atualizada!")
        
        # Regista no ficheiro de log que a password desta conta específica foi alterada.
        registar_log(FICHEIRO_LOG_USERS, "ALTERAÇÃO", f"Palavra-passe da conta '{nome_conta}' (ID: {id_editar}) alterada.")
        
    except Exception as e:
        print(f"Erro ao editar utilizador: {e}")
    finally:
        conn.close()


def limpar_divida_utilizador() -> None:
    """
    NOVA FUNÇÃO: Administrador regista o pagamento limpando o histórico de consultas do utilizador.
    """
    # Mostra quem existe. Se não houver clientes, aborta.
    if not listar_utilizadores():
        return
        
    # Pergunta qual o ID alvo para limpar o saldo de consultas.
    id_limpar = input("\nDigita o ID do utilizador para limpar a dívida (ou 0 para cancelar): ").strip()
    if id_limpar == '0' or not id_limpar:
        return
        
    conn = conectar()
    if not conn:
        return
        
    try:
        cursor = conn.cursor()
        
        # Validar se o ID fornecido pertence a um utilizador válido e não é o administrador.
        cursor.execute("SELECT conta FROM utilizador WHERE id_utilizador = ? AND conta != 'admin'", (id_limpar,))
        resultado = cursor.fetchone()
        
        if not resultado:
            print("Erro: ID inválido.")
            return
            
        nome_conta = resultado[0] # Guarda o nome para uso no log e nos 'prints'.
        
        # Apagar as consultas associadas ao utilizador (zerar a dívida)
        # Ao apagar da tabela 'consulta' com este ID, apagam-se todas as faturas financeiras deste utilizador.
        cursor.execute("DELETE FROM consulta WHERE id_utilizador = ?", (id_limpar,))
        # A propriedade .rowcount devolve a quantidade exata de linhas que foram afetadas pelo DELETE.
        linhas_apagadas = cursor.rowcount
        conn.commit() # Conclui o processo de eliminação.
        
        # Se apagou pelo menos 1 registo...
        if linhas_apagadas > 0:
            print(f"Sucesso: Dívida de '{nome_conta}' liquidada! ({linhas_apagadas} registos removidos)")
            # Audita a operação informando que o pagamento foi registado.
            registar_log(FICHEIRO_LOG_USERS, "PAGAMENTO", f"Dívida da conta '{nome_conta}' (ID: {id_limpar}) liquidada.")
        else:
            # Caso a tabela de consultas não tivesse nenhum registo ligado a este ID.
            print(f"O utilizador '{nome_conta}' não tinha dívidas pendentes.")
            
    except Exception as e:
        print(f"Erro ao limpar dívida: {e}")
    finally:
        conn.close()


def remover_utilizador() -> None:
    """Administrador apaga um utilizador, o seu histórico e regista no LOG."""
    # Lista quem pode ser apagado.
    if not listar_utilizadores():
        return
        
    # Recolhe o ID do azarado.
    id_remover = input("\nDigita o ID do utilizador a remover (ou 0 para cancelar): ").strip()
    if id_remover == '0' or not id_remover:
        return
        
    conn = conectar()
    if not conn:
        return
        
    try:
        cursor = conn.cursor()
        # Verifica se o alvo é legal (existe e não é admin).
        cursor.execute("SELECT conta FROM utilizador WHERE id_utilizador = ? AND conta != 'admin'", (id_remover,))
        resultado = cursor.fetchone()
        
        if not resultado:
            print("Erro: ID inválido ou tentativa de apagar o Administrador.")
            return
            
        nome_conta = resultado[0]
        
        # 1. Apagar primeiro o histórico de consultas para evitar erros de Foreign Key.
        # Em bases de dados relacionais, uma tabela pai (utilizador) não pode ser apagada se uma tabela filha (consulta) ainda estiver agarrada a ela. Por isso, apagamos as "filhas" primeiro.
        cursor.execute("DELETE FROM consulta WHERE id_utilizador = ?", (id_remover,))
        
        # 2. Apagar o utilizador. Agora que já não tem dependências financeiras ou de histórico penduradas no sistema.
        cursor.execute("DELETE FROM utilizador WHERE id_utilizador = ?", (id_remover,))
        
        conn.commit() # Fecha a transação tornando tudo oficial no disco.
        print(f"Sucesso: Utilizador '{nome_conta}' e o seu histórico foram removidos!")
        
        # Regista de imediato no ficheiro de texto da auditoria.
        registar_log(FICHEIRO_LOG_USERS, "REMOÇÃO", f"Conta '{nome_conta}' (ID: {id_remover}) apagada.")
        
    except Exception as e:
        print(f"Erro ao remover utilizador: {e}")
    finally:
        conn.close()


def menu_gerir_utilizadores() -> None:
    """Sub-menu para a gestão de utilizadores."""
    # Inicia um laço de repetição infinito (loop) para manter o menu funcional até o administrador pedir para sair.
    while True:
        # Desenha as opções do menu no ecrã.
        print("\n=== GERIR UTILIZADORES ===")
        print("1. Listar Utilizadores")
        print("2. Adicionar Utilizador")
        print("3. Editar Utilizador (Palavra-passe)")
        print("4. Remover Utilizador")
        print("5. Registar Pagamento (Limpar Dívida)") # Nova Opção!
        print("6. Visualizar LOGs no Terminal")
        print("7. Voltar ao Painel Geral")
        
        # Captura o texto escrito pelo admin e remove os espaços.
        escolha = input("Opção: ").strip()
        
        # Estrutura de condições ('if'/'elif') para direcionar a execução para a função correspondente ao número escolhido.
        if escolha == '1':
            listar_utilizadores()
        elif escolha == '2':
            adicionar_utilizador()
        elif escolha == '3':
            editar_utilizador()
        elif escolha == '4':
            remover_utilizador()
        elif escolha == '5':
            limpar_divida_utilizador()
        elif escolha == '6':
            ver_logs_no_terminal()
        elif escolha == '7':
            # Se escolher 7, o comando 'break' rebenta o ciclo 'while True', permitindo que a função termine e volte ao menu principal de onde foi chamada.
            break
        else:
            # Qualquer texto ou número fora dos esperados cai aqui.
            print("Opção inválida!")