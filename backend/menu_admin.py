# Importa a função 'menu_gerir_utilizadores' do módulo local 'backend.gerir_utilizadores'. Esta função contém o submenu responsável por adicionar, editar ou remover utilizadores.
from backend.gerir_utilizadores import menu_gerir_utilizadores
# Importa a função 'menu_gerir_jogos' do módulo 'backend.gerir_jogos', que gere o submenu de inserção, alteração e remoção dos jogos e respetivos resultados.
from backend.gerir_jogos import menu_gerir_jogos
# Importa a função 'ver_dividas_usuarios' do módulo financeiro ('backend.gerir_financas') para apresentar o balanço e lucros gerados pela plataforma.
from backend.gerir_financas import ver_dividas_usuarios
# Importa a função 'correr_testes_integridade' do módulo 'backend.testes_integridade', responsável por auditar a base de dados em busca de anomalias (como referências "órfãs" a dados apagados).
from backend.testes_integridade import correr_testes_integridade 
# Importa a função 'menu_gestao_avancada' do módulo 'backend.gestao_avancada' para dar acesso ao submenu focado na gestão desportiva (equipas, jogadores, golos).
from backend.gestao_avancada import menu_gestao_avancada


# Define a função principal que fará arrancar a interface de administração. A anotação '-> None' indica que a função executa um processo, mas não devolve nenhum dado de volta ao sistema.
def arrancar_menu_admin() -> None:
    """
    Menu principal de navegação para o Administrador.
    Executa uma auditoria de integridade à base de dados logo no arranque.
    """
    # Imprime uma mensagem informativa na consola a avisar o administrador de que uma verificação de segurança está em curso.
    print("\n[Sistema] A verificar a integridade da base de dados antes de iniciar...")
    
    # Chamada automática da função de testes ao entrar no painel
    # Corre o script de verificação importado em cima. Isto garante que não há ficheiros corrompidos ou erros na base de dados antes de o utilizador começar a trabalhar.
    correr_testes_integridade()
    
    # Inicia um ciclo infinito (loop 'while True') que mantém o menu constantemente ativo no ecrã até que o administrador decida sair voluntariamente.
    while True:
        # Desenha a margem superior do menu administrativo usando 50 sinais de igual. A quebra de linha '\n' assegura que o menu não fica "colado" ao texto anterior.
        print("\n" + "="*50)
        # Exibe o título do painel principal.
        print("PAINEL DE ADMINISTRADOR GERAL")
        # Desenha a margem inferior para encerrar o cabeçalho.
        print("="*50)
        
        # Apresenta sequencialmente as opções disponíveis, associando um número a cada funcionalidade.
        print("1. Gerir Jogos (Inserir/Alterar/Remover)")
        print("2. Gerir Utilizadores e LOGs")
        print("3. Visualizar Dívidas e Receita Global")
        print("4. Gestão Avançada (Equipas, Jogadores, Golos)")
        print("5. Logout (Voltar ao Menu Principal)")
        
        # Pede ao administrador que escreva um número. O método '.strip()' é aplicado imediatamente para remover quaisquer espaços vazios que tenham sido digitados sem querer antes ou depois do número.
        escolha = input("Escolhe uma opção: ").strip()
        
        # Estrutura de ramificação condicional para lidar com a escolha do utilizador.
        # Se o utilizador digitou '1', o programa entra neste bloco.
        if escolha == '1':
            # Imprime no ecrã a indicação de transição de menu.
            print("\n--> A abrir submenu de Jogos...")
            # Invoca a função importada que vai renderizar o submenu dos jogos e assumir o controlo até ser fechada.
            menu_gerir_jogos()
            
        # Caso o utilizador tenha digitado '2', transita para o bloco de utilizadores.
        elif escolha == '2':
            # Confirmação visual no terminal da ação solicitada.
            print("\n--> A abrir submenu de Utilizadores...")
            # Invoca a função que desenha e gere o menu das contas e respetivas passwords ou eliminações.
            menu_gerir_utilizadores()
            
        # Se a opção escolhida foi a '3', entra no bloco das finanças.
        elif escolha == '3':
            # Imprime o aviso de carregamento.
            print("\n--> A carregar relatórios financeiros...")
            # Invoca a função que vai fazer os cálculos matemáticos do dinheiro angariado e imprimir as faturas.
            ver_dividas_usuarios()
            
        # Se escolheu a opção '4', vai para a gestão aprofundada de base de dados.
        elif escolha == '4':
            # Confirma a mudança para as métricas avançadas de futebol.
            print("\n--> A abrir submenu de Gestão Avançada...")
            # Chama a função que congrega o menu para adicionar clubes, inserir atletas ou assinalar novos golos num jogo.
            menu_gestao_avancada()
            
        # A opção '5' encarrega-se do fim de sessão (logout).
        elif escolha == '5':
            # Imprime uma mensagem de despedida do painel central.
            print("\nA encerrar sessão de Administrador...")
            # O comando 'break' rebenta e quebra imediatamente o ciclo infinito 'while True' inicial. Como não há mais código depois deste ciclo, a função 'arrancar_menu_admin' chega ao fim e "devolve" o controlo ao script inicial que a chamou.
            break
            
        # Bloco "apanha-tudo" ('else'). Se o utilizador escrever letras, caracteres especiais ou números fora da lista (ex: "6", "A", etc.), o código cai aqui para evitar que o programa bloqueie.
        else:
            # Informa que a inserção não é reconhecida, após o qual o ciclo 'while' recomeça e volta a desenhar o menu principal desde o início.
            print("Opção inválida! Tenta novamente.")