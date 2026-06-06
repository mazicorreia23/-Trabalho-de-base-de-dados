import cloudscraper
from bs4 import BeautifulSoup
import re

# Dicionário que mapeia o nome das equipas (e as suas possíveis variações) 
# para o seu respetivo ID na base de dados relacional.
mapa_equipas = {
    "FC Porto": 1, "Sporting CP": 2, "Benfica": 3, "SL Benfica": 3,
    "SC Braga": 4, "FC Famalicão": 5, "Famalicão": 5, "Gil Vicente FC": 6, 
    "Gil Vicente": 6, "Estoril Praia": 7, "Estoril": 7, "Moreirense FC": 8, "Moreirense": 8,
    "Vitória SC": 9, "Vitória Guimarães": 9, "FC Arouca": 10, "Arouca": 10,
    "FC Alverca": 11, "Alverca": 11, "Rio Ave FC": 12, "Rio Ave": 12,
    "CF Estrela": 13, "Estrela Amadora": 13, "Estrela": 13, "CD Santa Clara": 14, "Santa Clara": 14,
    "CD Nacional": 15, "Nacional": 15, "Casa Pia AC": 16, "Casa Pia": 16,
    "CD Tondela": 17, "Tondela": 17, "AVS Futebol SAD": 18, "AVS Futebol": 18, "AVS": 18
}

def obter_id_equipa(nome_equipa_site):
    """
    Função auxiliar para encontrar o ID da equipa com base no nome extraído do site.
    Converte ambos os nomes para minúsculas para evitar erros de formatação.
    """
    for nome_conhecido, id_eq in mapa_equipas.items():
        if nome_conhecido.lower() in nome_equipa_site.lower():
            return id_eq
    return "NULL" # Retorna "NULL" (texto) para ser injetado no SQL caso não encontre correspondência

def extrair_jogos(url):
    """
    Função principal que faz o web scraping da página, extrai os dados dos jogos
    e gera comandos SQL INSERT para popular a base de dados.
    """
    # Cria uma instância do cloudscraper simulando ser um navegador Chrome no Windows.
    # Isto é crucial para ultrapassar as proteções anti-bot (Cloudflare) do Transfermarkt.
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    # Tenta fazer o pedido HTTP à página
    try:
        response = scraper.get(url)
    except Exception as e:
        print(f"-- ERRO de ligação: {e} --")
        return

    # Processa o conteúdo HTML devolvido usando o BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # --- Verificação Anti-Bot ---
    # Verifica se o título da página contém "Just a moment" (página de desafio do Cloudflare)
    # ou se o código de estado HTTP é 403 (Forbidden/Proibido).
    titulo = soup.title.get_text() if soup.title else ""
    if "Just a moment" in titulo or response.status_code == 403:
        print("-- ERRO: O sistema Anti-Bot (Cloudflare) bloqueou o pedido. Tenta novamente daqui a pouco. --")
        return

    print(f"-- SQL PARA A TABELA JOGO (URL: {url}) --\n")
    
    # Encontra todas as linhas de tabela (tags <tr>) no HTML
    linhas = soup.find_all("tr")
    jogos_gerados = 0
    data_atual = '2025-08-01' # Data por defeito caso a extração falhe na primeira jornada
    
    # Itera sobre cada linha da tabela
    for linha in linhas:
        colunas = linha.find_all("td") # Extrai as colunas da linha atual
        
        # 1. Extração da Data do Jogo
        for col in colunas:
            texto_coluna = col.get_text(strip=True)
            # Usa Expressões Regulares (Regex) para procurar datas no formato DD/MM/AA ou DD/MM/AAAA
            match_data = re.search(r'(\d{2})/(\d{2})/(\d{2,4})', texto_coluna)
            if match_data:
                dia, mes, ano = match_data.groups()
                # Se o ano tiver apenas 2 dígitos (ex: 25), converte para 4 dígitos (ex: 2025)
                if len(ano) == 2:
                    ano = f"20{ano}"
                # Formata a data para o padrão SQL (YYYY-MM-DD)
                data_atual = f"{ano}-{mes}-{dia}"
                break # Pára de procurar colunas mal encontre a data
                
        # 2. Extração do Resultado
        # Procura um link (tag <a>) que contenha "spielbericht" (relatório de jogo em alemão) no atributo href
        link_resultado = linha.find("a", href=lambda href: href and "spielbericht" in href)
        if not link_resultado:
            continue # Salta para a próxima linha se não for um jogo com resultado
            
        resultado = link_resultado.get_text(strip=True)
        # Garante que o texto tem o formato de resultado (ex: "2:1")
        if ":" not in resultado:
            continue
            
        # Separa os golos da equipa da casa e da equipa visitante
        try:
            golos = resultado.split(":")
            golos_casa = int(golos[0].strip())
            golos_fora = int(golos[1].strip())
        except ValueError:
            continue # Ignora se houver um erro de conversão (ex: jogo adiado)

        # 3. Extração dos Nomes das Equipas
        # Procura links (tag <a>) que contenham "verein" (clube) no href
        links_equipas = linha.find_all("a", href=lambda href: href and "verein" in href)
        nomes_equipas = []
        for link in links_equipas:
            nome = link.get('title') # O nome do clube costuma estar no atributo 'title'
            if nome and nome not in nomes_equipas:
                nomes_equipas.append(nome)
                
        # 4. Processamento e Geração de SQL
        # Se encontrou as duas equipas (casa e fora)
        if len(nomes_equipas) >= 2:
            # O Transfermarkt por vezes coloca a posição da equipa antes do nome, ex: "(1.) FC Porto".
            # O Regex re.sub(r'\(\d+\.\)', '', ...) remove esses parênteses e números.
            nome_casa = re.sub(r'\(\d+\.\)', '', nomes_equipas[0]).strip()
            nome_fora = re.sub(r'\(\d+\.\)', '', nomes_equipas[1]).strip()
            
            # Vai buscar os IDs correspondentes usando a função auxiliar
            id_casa = obter_id_equipa(nome_casa)
            id_fora = obter_id_equipa(nome_fora)
            
            # Define de forma simplificada o local do jogo com base na equipa da casa
            local_jogo = f"Estádio do {nome_casa}"
            
            # Constrói a query SQL de inserção
            sql = f"INSERT INTO jogo (data, local, id_equipa_casa, id_equipa_fora, golos_casa, golos_fora) VALUES ('{data_atual}', '{local_jogo}', {id_casa}, {id_fora}, {golos_casa}, {golos_fora});"
            
            # Imprime o comando diretamente no terminal
            print(sql)
            jogos_gerados += 1

    print(f"\n-- Total de {jogos_gerados} jogos extraídos com sucesso! --")

# URL alvo: Calendário geral da Liga Portugal, época 2025/2026
url_alvo = "https://www.transfermarkt.com/liga-portugal/gesamtspielplan/wettbewerb/PO1/saison_id/2025"
extrair_jogos(url_alvo)