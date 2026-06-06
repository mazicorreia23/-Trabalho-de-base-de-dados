# Importa 'Optional' do módulo 'typing' para indicar que uma variável ou retorno pode ter um valor ou ser nula (None).
from typing import Optional
# Importa a função 'conectar' do ficheiro 'database' na pasta 'backend' para estabelecer a ligação à base de dados.
from backend.database import conectar
# Importa a função 'registar_log' para poder gravar no ficheiro de auditoria as ações críticas feitas pelos administradores.
from backend.gerir_utilizadores import registar_log


def listar_jogos() -> None:
    """Lista todos os jogos registados na base de dados com o nome das equipas."""
    # Tenta estabelecer a ligação à base de dados.
    conn = conectar()
    # Se a ligação falhar, interrompe a execução da função imediatamente.
    if not conn:
        return

    # Inicia um bloco 'try' para capturar e gerir possíveis erros durante a execução da operação na base de dados.
    try:
        # Cria o cursor que permite enviar comandos SQL para a base de dados.
        cursor = conn.cursor()
        # Define a query SQL. O uso de 'JOIN' liga a tabela 'jogo' à tabela 'equipa' duas vezes:
        # uma para ir buscar o nome da equipa da casa (e1) e outra para a equipa de fora (e2).
        # Os resultados são ordenados de forma descendente (DESC) pela data.
        query = """
        SELECT j.id_jogo, j.data, e1.nome, e2.nome, j.golos_casa, j.golos_fora 
        FROM jogo j
        JOIN equipa e1 ON j.id_equipa_casa = e1.id_equipa
        JOIN equipa e2 ON j.id_equipa_fora = e2.id_equipa
        ORDER BY j.data DESC
        """
        # Executa a query preparada acima.
        cursor.execute(query)
        # Extrai todos os registos devolvidos pela base de dados e guarda-os na lista 'jogos'.
        jogos = cursor.fetchall()
        
        # Imprime no ecrã um cabeçalho formatado para separar visualmente a lista.
        print("\n" + "-"*65)
        print("CALENDÁRIO E RESULTADOS DA LIGA")
        print("-" * 65)
        
        # Verifica se a lista de jogos está vazia.
        if not jogos:
            print("Ainda não existem jogos registados na liga.")
        else:
            # Percorre cada jogo obtido da base de dados.
            for j in jogos:
                # Desempacota o tuplo 'j' atribuindo cada valor à sua respetiva variável.
                id_jogo, data, eq_casa, eq_fora, g_casa, g_fora = j
                # Usa um operador ternário: se 'g_casa' tiver um valor, mantém-no; se for nulo (None), coloca um traço "-".
                str_g_casa = g_casa if g_casa is not None else "-"
                # Faz o mesmo processo para os golos da equipa visitante.
                str_g_fora = g_fora if g_fora is not None else "-"
                # Imprime a linha do jogo formatada. O '<3' assegura que o ID ocupe sempre pelo menos 3 espaços, alinhando o texto.
                print(f"ID: {id_jogo:<3} | Data: {data} | {eq_casa} {str_g_casa}-{str_g_fora} {eq_fora}")
                
    # Captura qualquer exceção não prevista.
    except Exception as e:
        # Imprime o erro técnico na consola para facilitar a resolução de problemas (debugging).
        print(f"Erro ao listar jogos: {e}")
    # O bloco 'finally' é sempre executado no final, havendo ou não erro.
    finally:
        # Fecha a ligação à base de dados para não desperdiçar recursos do sistema.
        conn.close()
        # Desenha a linha de fecho do calendário.
        print("-" * 65)


def inserir_jogo() -> None:
    """Administrador insere um novo jogo no sistema."""
    # Apresenta o cabeçalho indicativo da ação.
    print("\n-- INSERIR NOVO JOGO --")
    # Pede ao utilizador a data e remove espaços em branco acidentais nas extremidades com '.strip()'.
    data = input("Data (YYYY-MM-DD): ").strip()
    # Pede o local do jogo e remove espaços desnecessários.
    local = input("Local (Ex: Estádio da Luz): ").strip()
    
    # Inicia a ligação.
    conn = conectar()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        # Mostra as equipas para o Admin saber os IDs
        # Executa uma pequena consulta para listar as equipas por ordem alfabética.
        cursor.execute("SELECT id_equipa, nome FROM equipa ORDER BY nome")
        print("\nEquipas Disponíveis:")
        # Percorre as equipas e imprime o ID e o Nome para auxiliar na escolha.
        for id_equipa, nome in cursor.fetchall():
            print(f"ID {id_equipa}: {nome}")
            
        # Pede os identificadores (IDs) de ambas as equipas.
        id_casa = input("\nID da Equipa da Casa: ").strip()
        id_fora = input("ID da Equipa de Fora: ").strip()
        
        # Validação básica para impedir equipas iguais
        # Verifica se o administrador introduziu o mesmo ID para a equipa de casa e visitante.
        if id_casa == id_fora:
            print("Erro: A equipa da casa não pode ser a mesma que a equipa de fora!")
            return # Cancela a operação se a condição de erro se verificar.

        # Pede os golos, mas permite que o campo fique em branco caso o jogo esteja agendado para o futuro.
        input_g_casa = input("Golos Casa (Deixa em branco se ainda não aconteceu): ").strip()
        input_g_fora = input("Golos Fora (Deixa em branco se ainda não aconteceu): ").strip()
        
        # Proteção contra ValueError (letras em vez de números)
        # Se o utilizador digitou algo, converte para número inteiro (int). Se não digitou nada, assume o valor nulo (None).
        g_casa = int(input_g_casa) if input_g_casa else None
        g_fora = int(input_g_fora) if input_g_fora else None
        
        # Executa o comando de inserção de dados. O uso das interrogações '?' protege contra ataques de injeção de SQL.
        cursor.execute("""
            INSERT INTO jogo (data, local, id_equipa_casa, id_equipa_fora, golos_casa, golos_fora) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data, local, id_casa, id_fora, g_casa, g_fora))
        
        # Valida e consolida as alterações definitivamente na base de dados.
        conn.commit()
        print("Sucesso: Novo jogo inserido na liga!")
        # Regista a operação no ficheiro de logs para auditoria futura, indicando a ação e as equipas envolvidas.
        registar_log("auditoria_jogos.log", "INSERÇÃO", f"Jogo inserido: Equipa {id_casa} vs Equipa {id_fora}")
        
    # Se o 'int()' falhar (por exemplo, se o utilizador escrever texto em vez de números nos golos), este bloco captura o erro.
    except ValueError:
        print("Erro: Os IDs das equipas e os golos devem ser números inteiros!")
    # Captura outros erros genéricos.
    except Exception as e:
        print(f"Erro ao inserir jogo: {e}")
    # Encerra sempre a comunicação de dados no fim.
    finally:
        conn.close()


def atualizar_placar() -> None:
    """Administrador altera o placar de um jogo existente."""
    # Invoca a função 'listar_jogos' para o administrador ver todos os jogos e saber o ID pretendido.
    listar_jogos()
    
    # Pede o ID do jogo a atualizar, com a opção de escrever '0' para desistir da ação.
    id_jogo = input("\nDigita o ID do jogo para atualizar o placar (ou 0 para cancelar): ").strip()
    if id_jogo == '0': 
        return # Abandona a função imediatamente.
    
    # Pede os novos valores para os golos.
    input_g_casa = input("Novos golos da equipa da casa: ").strip()
    input_g_fora = input("Novos golos da equipa de fora: ").strip()
    
    conn = conectar()
    if not conn:
        return

    try:
        # Validar numéricos rigorosamente para os golos numa atualização
        # Aqui força a conversão, gerando erro automático (ValueError) caso o utilizador tenha deixado em branco ou escrito texto.
        g_casa = int(input_g_casa)
        g_fora = int(input_g_fora)
        
        cursor = conn.cursor()
        
        # Verifica se o jogo existe antes de tentar atualizar
        # Faz uma pesquisa rápida só pelo ID do jogo.
        cursor.execute("SELECT id_jogo FROM jogo WHERE id_jogo = ?", (id_jogo,))
        # Se 'fetchone()' não encontrar nenhum registo correspondente...
        if not cursor.fetchone():
            print("Erro: O ID do jogo fornecido não existe.")
            return # Cancela a operação, pois o jogo não é válido.
            
        # Executa o comando UPDATE para modificar unicamente as colunas de golos do jogo específico.
        cursor.execute("UPDATE jogo SET golos_casa = ?, golos_fora = ? WHERE id_jogo = ?", (g_casa, g_fora, id_jogo))
        # Guarda as alterações.
        conn.commit()
        print("Sucesso: Placar atualizado de forma oficial!")
        # Cria uma entrada no log indicando que o placar foi alterado.
        registar_log("auditoria_jogos.log", "ALTERAÇÃO", f"Placar do jogo ID {id_jogo} atualizado para {g_casa}-{g_fora}")
        
    # Se a conversão 'int()' tiver falhado acima, informa o utilizador do motivo.
    except ValueError:
        print("Erro: O placar deve conter apenas valores numéricos!")
    except Exception as e:
        print(f"Erro ao atualizar placar: {e}")
    finally:
        conn.close()


def remover_jogo() -> None:
    """Administrador apaga um jogo registado e os seus respetivos golos."""
    # Lista os jogos para facilitar a visualização antes de apagar.
    listar_jogos()
    
    # Pede o ID do jogo a apagar, ou '0' para recuar.
    id_jogo = input("\nDigita o ID do jogo que pretendes remover (ou 0 para cancelar): ").strip()
    if id_jogo == '0':
        return
        
    conn = conectar()
    if not conn:
        return
        
    try:
        cursor = conn.cursor()
        
        # Verifica se o jogo existe
        cursor.execute("SELECT id_jogo FROM jogo WHERE id_jogo = ?", (id_jogo,))
        # Se a busca devolver vazio, informa que não existe e aborta.
        if not cursor.fetchone():
            print("Erro: O ID do jogo fornecido não existe.")
            return
            
        # Como ativámos as Foreign Keys no database.py (PRAGMA foreign_keys = ON),
        # apagar o jogo pode exigir apagar primeiro os golos a ele associados 
        # (caso não tenhas ON DELETE CASCADE na criação da tabela golo).
        # Para ser seguro, apagamos explícitamente na ordem certa:
        # 1º: Remove todos os eventos (golos) que dependem e pertencem a este jogo.
        cursor.execute("DELETE FROM golo WHERE id_jogo = ?", (id_jogo,))
        # 2º: Remove o registo do jogo em si, uma vez que já não tem dependências.
        cursor.execute("DELETE FROM jogo WHERE id_jogo = ?", (id_jogo,))
        
        # Consolida a dupla eliminação.
        conn.commit()
        print(f"Sucesso: O jogo ID {id_jogo} e os seus eventos foram removidos!")
        # Regista a eliminação no ficheiro de auditoria.
        registar_log("auditoria_jogos.log", "REMOÇÃO", f"Jogo ID {id_jogo} apagado do sistema.")
        
    except Exception as e:
        print(f"Erro ao remover jogo: {e}")
    finally:
        conn.close()


def menu_gerir_jogos() -> None:
    # Inicia um ciclo infinito (loop) para manter o menu ativo até que o utilizador decida sair.
    while True:
        # Imprime as opções do menu no ecrã.
        print("\n=== GERIR JOGOS ===")
        print("1. Listar todos os Jogos")
        print("2. Inserir Novo Jogo")
        print("3. Atualizar Placar de um Jogo")
        print("4. Remover Jogo")
        print("5. Voltar ao Painel Geral")
        
        # Recolhe a escolha do utilizador limpando possíveis espaços.
        escolha = input("Opção: ").strip()
        
        # Estrutura de decisão que encaminha o utilizador para a função apropriada com base na escolha numérica.
        if escolha == '1': 
            listar_jogos()
        elif escolha == '2': 
            inserir_jogo()
        elif escolha == '3': 
            atualizar_placar()
        elif escolha == '4': 
            remover_jogo()
        elif escolha == '5': 
            # O comando 'break' interrompe o 'while True', encerrando o menu e devolvendo o fluxo ao painel anterior.
            break
        else: 
            # Caso o utilizador insira uma letra ou um número fora do espectro 1-5.
            print("Opção inválida!")