# Importa as funções 'registar_utilizador' e 'fazer_login' do módulo de segurança 'backend.auth'. Estas tratam da criação de novas contas e da validação de credenciais, respetivamente.
from backend.auth import registar_utilizador, fazer_login
# Importa a função responsável por construir e gerir o painel de controlo exclusivo do administrador.
from backend.menu_admin import arrancar_menu_admin
# Importa a função que apresenta e gere a interface destinada aos utilizadores normais do sistema.
from backend.menu_user import arrancar_menu_user

# Define a função raiz da aplicação. O indicativo '-> None' serve de anotação de tipo, sinalizando que a função cumpre o seu propósito sem devolver dados no seu final.
def arrancar_menu() -> None:
    """
    Ponto de entrada principal do sistema.
    Gere o login, registo e encaminha o utilizador para o painel correto.
    """
    # Inicia um ciclo infinito (loop) para que o programa não termine repentinamente após executar um único comando. O menu continuará a surgir até o utilizador pedir explicitamente para sair.
    while True:
        # A quebra de linha '\n' aliada à multiplicação da string cria uma margem superior distanciada do texto anterior.
        print("\n" + "="*40)
        # Imprime o título do programa no ecrã (consola).
        print("LIGA DE FUTEBOL")
        # Desenha a margem inferior para fechar o cabeçalho.
        print("="*40)
        # Lista as opções disponíveis numeradas para o utilizador escolher.
        print("1. Login")
        print("2. Sign Up (Registar)")
        print("3. Sair do Sistema")
        
        # Pede uma instrução ao utilizador. A função nativa '.strip()' limpa silenciosamente quaisquer espaços em branco que o utilizador possa ter introduzido por acidente nas extremidades do texto.
        escolha = input("Escolhe uma opção: ").strip()
        
        # Inicia a estrutura de avaliação da opção selecionada. Se a escolha for '1', trata do processo de entrada.
        if escolha == '1':
            # Pede o nome da conta e limpa espaços residuais.
            conta = input("Conta: ").strip()
            # Pede a senha. O '.strip()' também limpa espaços residuais, mas as maiúsculas/minúsculas da senha introduzida mantêm-se inalteradas para garantir a exatidão criptográfica.
            senha = input("Palavra-passe: ").strip() # Aqui mantemos a senha original (com maiúsculas/minúsculas)
            
            # Validação rápida para evitar idas desnecessárias à BD
            # Verifica se algum dos campos ficou completamente vazio. O 'not' avalia strings vazias ("") como Falsas.
            if not conta or not senha:
                # Avisa o utilizador da omissão.
                print("Erro: A conta e a palavra-passe são obrigatórias!")
                # O comando 'continue' força o programa a saltar todo o código que se segue abaixo e a recomeçar o ciclo 'while' de imediato (voltando a mostrar o menu inicial).
                continue
                
            # Chama a função de autenticação passando os dados introduzidos. O resultado (ex: 'admin', 'user', ou None) é armazenado na variável 'tipo_acesso'.
            tipo_acesso = fazer_login(conta, senha)
            
            # Avalia se a credencial devolvida pelo sistema de autenticação pertence ao administrador.
            if tipo_acesso == 'admin':
                # Mensagem de transição.
                print("\n--> A redirecionar para o Painel de Administrador...")
                # Passa o controlo do programa para a função do menu de administrador (o programa "entra" nesta função e fica lá até o admin fazer logout).
                arrancar_menu_admin()
            # Avalia se a credencial é a de um utilizador comum.
            elif tipo_acesso == 'user':
                # Mensagem de transição personalizada. O '.upper()' capitaliza o nome da conta para dar destaque visual (ex: "Bem-vindo JOÃO").
                print(f"\n--> A redirecionar para o Menu de Consultas de {conta.upper()}...")
                # Passa o controlo para o menu do utilizador, injetando na função a variável 'conta' para que o sistema saiba a quem pertencem os dados que vai carregar.
                arrancar_menu_user(conta)
                
        # Se a opção inicial no menu principal foi a '2', o foco é a criação de conta.
        elif escolha == '2':
            # Cabeçalho para identificar a área de registo.
            print("\n-- NOVO REGISTO --")
            # Solicita o nome desejado.
            conta = input("Escolhe a tua Conta: ").strip()
            # Solicita a senha a associar.
            senha = input("Escolhe a tua Palavra-passe: ").strip()
            
            # Impede registos em branco
            # Avalia se houve alguma introdução em branco por parte do utilizador.
            if not conta or not senha:
                # Informa que não é possível registar "nada".
                print("Erro: A conta e a palavra-passe não podem estar vazias!")
            # Se a validação for superada (ambos os campos preenchidos).
            else:
                # Aciona o motor de base de dados encarregue de guardar permanentemente as informações.
                registar_utilizador(conta, senha)
                
        # Se a opção escolhida for a '3', a intenção é desligar o programa.
        elif escolha == '3':
            # Despede-se do utilizador.
            print("\nA sair do sistema... Até logo!")
            # O comando 'break' destrói o ciclo infinito ('while True'). Como esta função não tem mais linhas a seguir ao ciclo, a execução termina e o programa encerra.
            break
            
        # Caso o utilizador tecle qualquer coisa diferente de '1', '2' ou '3' (por exemplo, letras, outros números ou vazios).
        else:
            # Imprime uma mensagem de erro e, de seguida, o ciclo recomeça, oferecendo o menu outra vez.
            print("Opção inválida! Tenta novamente.")