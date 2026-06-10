import sqlite3
import random

# Define o caminho absoluto para o ficheiro da base de dados do projeto
CAMINHO_BD = 'BD\liga_futebol.db'

def gerar_golos():
    try:
        # Estabelece a ligação à base de dados SQLite
        conn = sqlite3.connect(CAMINHO_BD)
        cursor = conn.cursor()

        # Seleciona apenas os jogos que já têm um resultado definido (onde os golos não são nulos)
        cursor.execute("SELECT id_jogo, id_equipa_casa, id_equipa_fora, golos_casa, golos_fora FROM jogo WHERE golos_casa IS NOT NULL")
        jogos = cursor.fetchall()

        # Informa o utilizador no terminal sobre o número de jogos encontrados
        print(f"--> O script encontrou {len(jogos)} jogos na base de dados.")
        
        # Validação de segurança: se a tabela estiver vazia, avisa o utilizador e interrompe o script
        if len(jogos) == 0:
            print("PARAGEM: A tua tabela 'jogo' está vazia no ficheiro. Volta ao DB Browser, garante que fizeste os INSERTs e clica em 'Write Changes' (Escrever Alterações) lá no topo!")
            return

        # Variável para contabilizar o número total de golos que serão inseridos na tabela
        total_golos_inseridos = 0

        # Itera sobre cada jogo recuperado da base de dados
        for jogo in jogos:
            # Desempacota os dados do jogo em variáveis individuais para facilitar a leitura
            id_jogo, id_casa, id_fora, golos_casa, golos_fora = jogo

            # FUNÇÃO AUXILIAR: Obtém a lista de jogadores de uma determinada equipa
            def obter_jogadores(id_equipa):
                cursor.execute("SELECT id_jogador, posicao FROM jogador WHERE id_equipa = ?", (id_equipa,))
                return cursor.fetchall()

            # Vai buscar os planteis das duas equipas envolvidas no jogo atual
            jogadores_casa = obter_jogadores(id_casa)
            jogadores_fora = obter_jogadores(id_fora)

            # Verifica se as equipas têm jogadores. Se não tiverem, salta este jogo para evitar erros no sorteio
            if not jogadores_casa:
                print(f"AVISO: A equipa da casa (ID {id_casa}) não tem jogadores associados na base de dados. A saltar o jogo {id_jogo}...")
                continue
            if not jogadores_fora:
                print(f"AVISO: A equipa de fora (ID {id_fora}) não tem jogadores associados na base de dados. A saltar o jogo {id_jogo}...")
                continue

            # FUNÇÃO AUXILIAR: Simula a autoria e o minuto de cada golo, inserindo-os na base de dados
            def registar_golos(qnt_golos, jogadores):
                golos_marcados = 0
                for _ in range(qnt_golos):
                    # Gera um minuto aleatório entre o início e eventuais descontos (98 min)
                    minuto = random.randint(1, 98)
                    
                    # Cria uma lista de pesos para aumentar a probabilidade de certos jogadores marcarem
                    pesos = []
                    for jog in jogadores:
                        if jog[1] == 'Avançado': pesos.append(50) # Maior probabilidade (50)
                        elif jog[1] == 'Médio': pesos.append(30)  # Probabilidade média (30)
                        elif jog[1] == 'Defesa': pesos.append(10) # Probabilidade baixa (10)
                        else: pesos.append(1)                     # Guarda-redes (Probabilidade muito baixa: 1)
                    
                    # Sorteia um jogador com base nos pesos atribuídos acima
                    escolhido = random.choices(jogadores, weights=pesos, k=1)[0]
                    id_jogador = escolhido[0] # Extrai o ID do jogador sorteado

                    # Insere o registo do golo na tabela 'golo'
                    cursor.execute(
                        "INSERT INTO golo (id_jogador, id_jogo, minuto) VALUES (?, ?, ?)",
                        (id_jogador, id_jogo, minuto)
                    )
                    golos_marcados += 1
                return golos_marcados

            # Se a equipa da casa marcou golos, chama a função para os registar
            if golos_casa > 0:
                total_golos_inseridos += registar_golos(golos_casa, jogadores_casa)
            
            # Se a equipa de fora marcou golos, chama a função para os registar
            if golos_fora > 0:
                total_golos_inseridos += registar_golos(golos_fora, jogadores_fora)

        # Guarda todas as inserções na base de dados de uma só vez (muito mais rápido do que fazer commit um a um)
        conn.commit()
        print(f"\nSUCESSO! Foram gerados e inseridos {total_golos_inseridos} golos na base de dados.")

    # Apanha eventuais erros do SQLite (ex: tabela não existe, erro de integridade) e imprime-os sem rebentar o programa
    except sqlite3.Error as e:
        print(f"Erro na base de dados SQLite: {e}")
    # O bloco finally garante que a ligação é fechada, quer o script corra bem, quer dê erro
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# Executa a função principal
gerar_golos()