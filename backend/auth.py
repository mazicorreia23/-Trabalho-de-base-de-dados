import hashlib # Importa o módulo nativo 'hashlib', que fornece algoritmos seguros de dispersão (hash) e de compressão de mensagens (como o SHA-256).
from typing import Optional # Importa 'Optional' do módulo 'typing', usado para indicar (type hint) que uma variável ou retorno pode ser de um tipo específico ou 'None'.
from backend.database import conectar # Importa a função 'conectar', proveniente de um módulo local do projeto ('backend.database'), responsável por inicializar a ligação à base de dados.

# --- CONSTANTES ---
# Centralizar estes valores em variáveis globais constantes evita escrever os valores várias vezes pelo código (hardcoding), facilitando muito a manutenção futura.
ADMIN_USERNAME = 'admin' # Define qual será o nome de utilizador específico reservado para conceder acessos máximos ao sistema.
ROLE_ADMIN = 'admin' # Palavra-chave (papel/permissão) devolvida pelo sistema quando quem faz login é o administrador.
ROLE_USER = 'user' # Palavra-chave (papel/permissão) devolvida pelo sistema quando quem faz login é um utilizador padrão.


def encriptar_senha(senha: str) -> str:
    """
    Esta função recebe uma palavra-passe legível (string) e devolve a sua representação criptográfica através de um hash unidirecional.
    Anotações (type hints) como 'senha: str -> str' ajudam a identificar o tipo de dados que entra e sai da função.
    """
    # 1. senha.encode('utf-8'): O algoritmo precisa de lidar com bytes e não com strings. Isto codifica o texto para bytes usando UTF-8.
    # 2. hashlib.sha256(...): Aplica o algoritmo de hash SHA-256 sobre esses bytes.
    # 3. .hexdigest(): Converte o resultado binário complexo numa string alfanumérica, legível e em formato hexadecimal.
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def registar_utilizador(conta: str, senha: str) -> bool:
    """
    Gere o fluxo completo de criação de um novo utilizador no sistema, validando nomes, 
    verificando duplicações e guardando de forma segura na base de dados.
    Devolve 'True' (Verdadeiro) se o processo chegar ao fim com sucesso, e 'False' (Falso) se falhar.
    """
    # Remove automaticamente espaços vazios (" ") que o utilizador possa ter inserido por acidente no início ou fim do nome (ex: " joao " passa a "joao").
    conta_limpa = conta.strip() 
    
    # --- VALIDAÇÃO DE SEGURANÇA ---
    # Verifica se o utilizador está a tentar registar-se com o nome reservado do sistema.
    # O uso do .lower() converte a palavra para minúsculas antes da comparação, garantindo que variações como "AdMiN" ou "ADMIN" também sejam bloqueadas.
    if conta_limpa.lower() == ADMIN_USERNAME: 
        print("Erro de Segurança: Não podes registar uma conta com o nome de Administrador!") 
        return False # Cancela imediatamente o registo devolvendo falso.

    # Solicita a ligação à base de dados através da função previamente importada.
    conn = conectar() 
    if not conn: # Testa se a ligação foi criada com sucesso; se não, 'conn' será um valor falso/inválido.
        return False # Cancela o registo, dado que sem base de dados é impossível guardar a conta.

    # O bloco 'try' (tentar) serve para embrulhar código que pode gerar quebras (ex: falha na rede ou na query).
    # Caso algo rebente lá dentro, o erro é capturado de forma controlada sem deitar o programa todo abaixo.
    try: 
        # O cursor é um objeto que serve de "mensageiro" entre o código Python e o motor da Base de Dados, permitindo executar comandos SQL.
        cursor = conn.cursor() 
        
        # Transforma imediatamente a palavra-passe legível introduzida pelo utilizador num código hash irreversível, garantindo a sua privacidade.
        senha_hash = encriptar_senha(senha) 
        
        # --- VERIFICAÇÃO DE CONTAS DUPLICADAS ---
        # Executa um comando SQL (SELECT) procurando por um utilizador com um nome equivalente.
        # Usa-se o LOWER() do lado do SQL e o .lower() no Python para garantir que as procuras não diferenciem maiúsculas de minúsculas (case-insensitive).
        # Os parênteses com vírgula `(conta_limpa.lower(),)` passam o valor de forma blindada contra injeções de SQL.
        cursor.execute("SELECT id_utilizador FROM utilizador WHERE LOWER(conta) = ?", (conta_limpa.lower(),))
        
        # fetchone() tenta extrair e ler o primeiro resultado obtido por esta pesquisa.
        if cursor.fetchone(): # Se for encontrado algum resultado de volta, o nome de conta já está ocupado por alguém.
            print("Erro: Esta conta já existe! Escolhe outro nome de utilizador.") 
            return False # Cancela o registo por duplicação.
            
        # --- GUARDA O NOVO UTILIZADOR ---
        # Prepara e executa o comando SQL (INSERT INTO) para adicionar uma nova linha à tabela 'utilizador', preenchendo as colunas 'conta' e 'palavra_passe'.
        # Volta a usar as interrogações `?` (parâmetros tipificados) por motivos de segurança (evitar SQL Injection).
        cursor.execute("INSERT INTO utilizador (conta, palavra_passe) VALUES (?, ?)", (conta_limpa, senha_hash))
        
        # O 'commit' consolida as alterações. Até o commit ser feito, as alterações vivem apenas em memória e não estão efetivamente gravadas no ficheiro da base de dados.
        conn.commit() 
        print(f"Sucesso: Utilizador '{conta_limpa}' registado com sucesso!") 
        return True # Assinala que todo o fluxo decorreu perfeitamente.
        
    except Exception as e: 
        # Bloco de exceção: Se qualquer linha dentro do 'try' falhar (exemplo, a tabela de destino não existe), o Python salta para aqui.
        # O erro exato é guardado na variável 'e' e impresso na consola, devolvendo False logo a seguir em vez de "crashar" o programa inteiro.
        print(f"Erro ao registar: {e}") 
        return False 
        
    finally: 
        # O bloco 'finally' (finalmente) é inevitável. Corre sempre, quer tenha havido sucesso, quer tenha ocorrido um erro ou retorno prematuro ('return').
        # A sua função primordial neste caso é encerrar a ligação à base de dados para não deixar recursos bloqueados ou conexões mortas ("memory leak").
        conn.close() 


def fazer_login(conta: str, senha: str) -> Optional[str]: 
    """
    Verifica se um utilizador existe e se introduziu a senha correta.
    Devolve uma string determinando o nível do utilizador (ex: 'admin' ou 'user') se houver sucesso na autenticação.
    Se o login falhar por algum motivo, devolve 'None' (nulo).
    """
    # Invoca a tentativa de conexão à base de dados.
    conn = conectar() 
    if not conn: # Sem ligação ativa, não é possível autenticar, recusa imediatamente a validação.
        return None 

    try: 
        # Inicia o cursor para comunicar com a base de dados em SQL.
        cursor = conn.cursor() 
        
        # Durante o login, recebemos do utilizador a senha em texto limpo.
        # Temos que aplicar a ela exatamente o mesmo processo matemático de hashing para comparar as duas versões encriptadas (a que acabámos de gerar com a que está salva na base de dados).
        senha_hash = encriptar_senha(senha) 
        
        # --- COMPARAÇÃO DE CREDENCIAIS ---
        # Executa uma busca estrita na tabela exigindo que os dois critérios (nome E palavra-passe) estejam simultaneamente preenchidos.
        cursor.execute("SELECT id_utilizador FROM utilizador WHERE conta = ? AND palavra_passe = ?", (conta, senha_hash))
        resultado = cursor.fetchone() # Puxa o resultado dessa busca.
        
        # Se 'resultado' vier vazio (False/None), é sinal que as credenciais providenciadas não batem certo com nenhum registo válido na base de dados.
        if not resultado: 
            print("Erro: Conta ou palavra-passe incorretos.") # Mantém a mensagem genérica para não revelar a potenciais atacantes qual dos dois elementos (nome ou senha) falhou.
            return None # Nega o acesso.
            
        print(f"\nBem-vindo, {conta}!") # Se passou do "if" acima, é porque o utilizador entrou com sucesso. Escreve uma mensagem de boas-vindas.
        
        # --- GESTÃO DE PERMISSÕES ---
        # Usa um "operador ternário" nativo do Python (valor_A if condicao else valor_B) para devolver uma resposta curta consoante a condição de forma limpa numa só linha.
        # Caso o nome de login introduzido seja idêntico à constante do admin, atribui a autoridade/papel máximo ('ROLE_ADMIN'). Para todos os outros casos atribui papel de utilizador padrão ('ROLE_USER').
        return ROLE_ADMIN if conta.lower() == ADMIN_USERNAME else ROLE_USER
        
    except Exception as e: 
        # Captura quebras técnicas não previstas (desconexões da base de dados, sintaxe SQL errada no código, etc).
        print(f"Erro crítico durante o login: {e}") 
        return None # Responde rejeitando o acesso, pois mais vale bloquear por precaução do que deixar passar um erro grave.
        
    finally: 
        # Como mandam as boas práticas, liberta os recursos fechando a conexão à base de dados no término da operação de leitura.
        conn.close()