import sqlite3 # Importa a biblioteca nativa do Python responsável por gerir bases de dados SQLite, permitindo executar operações SQL num ficheiro local.
import os # Importa o módulo 'os', que fornece funcionalidades para interagir com o sistema operativo, como a manipulação de caminhos, ficheiros e pastas.
from typing import Optional # Importa o 'Optional' do módulo de tipagem ('typing') para ajudar a documentar que uma função pode devolver um valor específico ou um valor nulo ('None').

# --- CONSTANTES DE CONFIGURAÇÃO ---
# Centralizar estes valores no início do ficheiro facilita a manutenção, evitando espalhar nomes e caminhos "hardcoded" pelo código afora.

PASTA_BD = 'BD' # Define o nome da pasta (diretoria) principal onde o ficheiro da base de dados vai residir.
# Constrói o caminho completo para o ficheiro da base de dados ('BD/liga_futebol.db').
# A função 'os.path.join' é usada por segurança, pois garante que o caminho é construído com as barras certas dependendo do sistema operativo (Windows usa '\', Linux/Mac usa '/').
NOME_BD = os.path.join(PASTA_BD, 'liga_futebol.db') 


def conectar() -> Optional[sqlite3.Connection]:
    """
    Função dedicada a criar e devolver a ligação à base de dados SQLite.
    Garante também que a diretoria necessária existe e aplica regras de integridade.
    O indicativo '-> Optional[sqlite3.Connection]' assinala que a função devolverá um objeto de ligação se tiver sucesso, ou 'None' se falhar.
    """
    
    # 1. Segurança de Infraestrutura:
    # A função 'makedirs' cria a pasta especificada na variável 'PASTA_BD'. 
    # O argumento 'exist_ok=True' é crucial: diz ao Python para ignorar o comando silenciosamente (não lançando erro) se a pasta já existir.
    os.makedirs(PASTA_BD, exist_ok=True)
    
    # O bloco 'try' inicia uma zona de execução protegida. Se algo falhar na ligação, o erro é apanhado sem fazer o programa ir abaixo (crash).
    try:
        # Tenta estabelecer a ligação com a base de dados usando o caminho definido acima.
        # Característica útil do SQLite: Se o ficheiro 'liga_futebol.db' não existir naquele local, ele será criado automaticamente e de imediato por este comando.
        conn = sqlite3.connect(NOME_BD)
        
        # 2. Integridade de Dados:
        # Por motivos históricos, o motor do SQLite não valida Chaves Estrangeiras (Foreign Keys) por predefinição.
        # A execução do comando "PRAGMA foreign_keys = ON" altera esse comportamento nesta ligação específica, forçando a base de dados a não permitir, por exemplo,
        # que se apague um registo que já esteja a ser referenciado e usado noutra tabela.
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Se as linhas acima correram bem, a função devolve o objeto de conexão ('conn') ativo e pronto a ser usado por outras funções do projeto.
        return conn
        
    # Se ocorrer algum erro técnico do lado da biblioteca do SQLite durante o bloco 'try' (ex: ficheiro corrompido, permissões negadas), o fluxo salta para aqui.
    # O erro específico é capturado na variável 'e'.
    except sqlite3.Error as e:
        # Imprime na consola uma mensagem de alerta bem visível e injeta o erro exato ('e') para facilitar a despistagem do problema (debugging).
        print(f"[ERRO CRÍTICO] Falha ao ligar à base de dados '{NOME_BD}': {e}")
        
        # Devolve um valor nulo indicando à parte do código que invocou esta função que a ligação não foi bem-sucedida.
        return None