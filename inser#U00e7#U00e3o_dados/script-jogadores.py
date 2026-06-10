import requests
from bs4 import BeautifulSoup

# Função para agrupar as várias posições específicas do Transfermarkt em 4 categorias principais
def mapear_posicao(posicao_original):
    # Converte o texto para minúsculas para facilitar a comparação
    pos = posicao_original.lower()
    
    # Verifica que palavras existem na posição detalhada e devolve a posição simplificada
    if 'guarda-redes' in pos: return 'Guarda-redes'
    if 'defesa' in pos or 'lateral' in pos: return 'Defesa'
    if 'médio' in pos or 'central' in pos or 'pivô' in pos: return 'Médio'
    if 'extremo' in pos or 'ponta de lança' in pos or 'avançado' in pos: return 'Avançado'
    
    # Se não encaixar em nenhuma das regras acima, devolve 'Outro'
    return 'Outro'

# Função principal que vai à página de uma equipa recolher os jogadores
def extrair_jogadores(url, id_equipa):
    # Falsifica o 'User-Agent' para que o Transfermarkt pense que o pedido vem de um navegador normal (Chrome/Firefox) e não bloqueie o script
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Faz o pedido HTTP (GET) à página
    response = requests.get(url, headers=headers)
    
    # Pega no código HTML recebido e converte-o num objeto "Soup", que permite pesquisar por tags HTML facilmente
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontra a tabela HTML que tem a classe 'items' (onde o Transfermarkt lista o plantel)
    tabela = soup.find("table", class_="items")
    
    # Dentro dessa tabela, encontra todas as linhas (tags <tr>) que tenham as classes 'odd' (ímpar) ou 'even' (par)
    linhas = tabela.find_all("tr", class_=["odd", "even"])
    
    # Imprime um cabeçalho no terminal para separar visualmente as equipas
    print(f"\n-- SQL PARA EQUIPA {id_equipa} --")
    
    # Itera sobre cada linha da tabela (cada linha corresponde a um jogador)
    for linha in linhas:
        try:
            # Procura a célula que contém o nome (classe 'hauptlink') e extrai o texto do link (tag <a>)
            nome_tag = linha.find("td", class_="hauptlink").find("a")
            # Extrai o nome, remove espaços extra (strip=True) e substitui plicas (') por duas plicas ('') para não rebentar a sintaxe do SQL
            nome = nome_tag.get_text(strip=True).replace("'", "''")
            
            # Vai buscar todas as células (<td>) desta linha para extrair os restantes dados
            pos_tag = linha.find_all("td")
            
            # A posição costuma estar na 5ª célula (índice 4). Se a linha tiver menos células, assume "N/A"
            pos_detalhada = pos_tag[4].get_text(strip=True) if len(pos_tag) > 4 else "N/A"
            # Chama a função lá de cima para converter a posição detalhada numa das 4 principais
            posicao_final = mapear_posicao(pos_detalhada)
            
            # A idade costuma estar na 6ª célula (índice 5)
            idade_texto = pos_tag[5].get_text(strip=True) if len(pos_tag) > 5 else "NULL"
            # Filtra o texto para manter apenas os números (remove parênteses ou texto extra). Se ficar vazio, assume "NULL"
            idade = "".join(filter(str.isdigit, idade_texto)) or "NULL"

            # Imprime o comando SQL (INSERT INTO) formatado e pronto a colar no DB Browser (ou DBeaver, etc.)
            print(f"INSERT INTO jogador (nome, posicao, idade, id_equipa) VALUES ('{nome}', '{posicao_final}', {idade}, {id_equipa});")
            
        # Se ocorrer algum erro ao ler a linha (ex: linha de formatação vazia), ignora e passa ao próximo jogador
        except Exception:
            continue

# Lista de dicionários contendo o link do plantel no Transfermarkt e o ID que a equipa tem na tua base de dados
equipas = [
    {"link": "https://www.transfermarkt.pt/fc-porto/kader/verein/720", "id": 1},
    {"link": "https://www.transfermarkt.pt/sporting-cp/kader/verein/336", "id": 2},
    {"link": "https://www.transfermarkt.pt/sl-benfica/kader/verein/294", "id": 3},
    {"link": "https://www.transfermarkt.pt/sc-braga/kader/verein/1075", "id": 4},
    {"link": "https://www.transfermarkt.pt/fc-famalicao/kader/verein/3329", "id": 5},
    {"link": "https://www.transfermarkt.pt/gil-vicente-fc/kader/verein/2424", "id": 6},
    {"link": "https://www.transfermarkt.pt/gd-estoril-praia/kader/verein/1465", "id": 7},
    {"link": "https://www.transfermarkt.pt/moreirense-fc/kader/verein/979", "id": 8},
    {"link": "https://www.transfermarkt.pt/vitoria-sc/kader/verein/2420", "id": 9},
    {"link": "https://www.transfermarkt.pt/fc-arouca/kader/verein/8024", "id": 10},
    {"link": "https://www.transfermarkt.pt/fc-alverca/kader/verein/2521", "id": 11},
    {"link": "https://www.transfermarkt.pt/rio-ave-fc/kader/verein/2425", "id": 12},
    {"link": "https://www.transfermarkt.pt/cf-estrela-amadora/kader/verein/2431", "id": 13},
    {"link": "https://www.transfermarkt.pt/cd-santa-clara/kader/verein/2423", "id": 14},
    {"link": "https://www.transfermarkt.pt/cd-nacional/kader/verein/982", "id": 15},
    {"link": "https://www.transfermarkt.pt/casa-pia-ac/kader/verein/3268", "id": 16},
    {"link": "https://www.transfermarkt.pt/cd-tondela/kader/verein/7179", "id": 17},
    {"link": "https://www.transfermarkt.pt/avs-futebol-sad/kader/verein/110302", "id": 18},
]

# Corre a lista e executa a função de extração para cada uma das equipas
for equipa in equipas:
    extrair_jogadores(equipa["link"], equipa["id"])