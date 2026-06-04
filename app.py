from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Mude isto em produção

# Caminho da base de dados
DATABASE = 'futebol.db'

def get_db_connection():
    """Cria uma conexão à base de dados com row factory ativado."""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar à base de dados: {e}")
        return None

def init_db():
    """Inicializa a base de dados com o esquema fornecido."""
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.executescript("""
                    CREATE TABLE equipa (
                        id_equipa INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        cidade TEXT,
                        treinador TEXT
                    );

                    CREATE TABLE jogador (
                        id_jogador INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        posicao TEXT,
                        idade INTEGER,
                        id_equipa INTEGER,
                        FOREIGN KEY (id_equipa) REFERENCES equipa(id_equipa)
                    );

                    CREATE TABLE jogo (
                        id_jogo INTEGER PRIMARY KEY AUTOINCREMENT,
                        data DATE NOT NULL,
                        local TEXT,
                        id_equipa_casa INTEGER,
                        id_equipa_fora INTEGER,
                        golos_casa INTEGER DEFAULT 0,
                        golos_fora INTEGER DEFAULT 0,
                        FOREIGN KEY (id_equipa_casa) REFERENCES equipa(id_equipa),
                        FOREIGN KEY (id_equipa_fora) REFERENCES equipa(id_equipa)
                    );

                    CREATE TABLE golo (
                        id_golo INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_jogador INTEGER,
                        id_jogo INTEGER,
                        minuto INTEGER,
                        FOREIGN KEY (id_jogador) REFERENCES jogador(id_jogador),
                        FOREIGN KEY (id_jogo) REFERENCES jogo(id_jogo)
                    );

                    CREATE TABLE utilizador (
                        id_utilizador INTEGER PRIMARY KEY AUTOINCREMENT,
                        conta TEXT UNIQUE NOT NULL,
                        palavra_passe TEXT NOT NULL
                    );

                    CREATE TABLE tipo_consulta (
                        id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
                        descricao TEXT NOT NULL,
                        custo REAL NOT NULL
                    );

                    CREATE TABLE consulta (
                        id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_utilizador INTEGER,
                        id_tipo INTEGER,
                        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id_utilizador) REFERENCES utilizador(id_utilizador),
                        FOREIGN KEY (id_tipo) REFERENCES tipo_consulta(id_tipo)
                    );

                    -- Inserir dados de exemplo
                    INSERT INTO equipa (nome, cidade, treinador) VALUES
                    ('Sporting CP', 'Lisboa', 'Rúben Amorim'),
                    ('SL Benfica', 'Lisboa', 'João Loureiro'),
                    ('FC Porto', 'Porto', 'Vítor Bruno'),
                    ('Braga', 'Braga', 'Carlos Carvalhal');

                    INSERT INTO jogador (nome, posicao, idade, id_equipa) VALUES
                    ('Cristiano Ronaldo', 'Avançado', 39, 2),
                    ('Bruno Fernandes', 'Médio', 29, 1),
                    ('Rúben Neves', 'Médio', 27, 3),
                    ('Abel Ruiz', 'Avançado', 25, 4),
                    ('Geraldes', 'Médio', 22, 1),
                    ('Diogo Costa', 'Guarda-redes', 23, 3);
                """)
                conn.commit()
                print("Base de dados inicializada com sucesso!")
            except sqlite3.Error as e:
                print(f"Erro ao inicializar a base de dados: {e}")
            finally:
                conn.close()

def get_equipas():
    """Obtém a lista de todas as equipas."""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            equipas = cursor.execute('SELECT id_equipa, nome FROM equipa ORDER BY nome').fetchall()
            conn.close()
            return equipas
    except sqlite3.Error as e:
        print(f"Erro ao obter equipas: {e}")
    return []

def get_jogadores_por_equipa(id_equipa):
    """Obtém todos os jogadores de uma equipa específica."""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            jogadores = cursor.execute(
                'SELECT id_jogador, nome, posicao, idade FROM jogador WHERE id_equipa = ? ORDER BY nome',
                (id_equipa,)
            ).fetchall()
            conn.close()
            return jogadores
    except sqlite3.Error as e:
        print(f"Erro ao obter jogadores: {e}")
    return []

def get_equipa_nome(id_equipa):
    """Obtém o nome da equipa pelo ID."""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            equipa = cursor.execute('SELECT nome FROM equipa WHERE id_equipa = ?', (id_equipa,)).fetchone()
            conn.close()
            return equipa[0] if equipa else None
    except sqlite3.Error as e:
        print(f"Erro ao obter nome da equipa: {e}")
    return None

def adicionar_jogador(nome, posicao, idade, id_equipa):
    """Adiciona um novo jogador à base de dados."""
    try:
        if not nome or not id_equipa:
            return False, "Nome e Equipa são obrigatórios"
        
        if idade and (idade < 16 or idade > 50):
            return False, "Idade deve estar entre 16 e 50 anos"
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO jogador (nome, posicao, idade, id_equipa) VALUES (?, ?, ?, ?)',
                (nome, posicao, idade if idade else None, id_equipa)
            )
            conn.commit()
            conn.close()
            return True, "Jogador adicionado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Erro: Jogador já existe ou dados inválidos"
    except sqlite3.Error as e:
        return False, f"Erro ao adicionar jogador: {e}"
    
    return False, "Erro desconhecido"

# Rotas

@app.route('/')
def index():
    """Página inicial."""
    equipas = get_equipas()
    return render_template('base.html', equipas=equipas)

@app.route('/jogadores', methods=['GET', 'POST'])
def jogadores():
    """Página de consulta de jogadores por equipa."""
    equipas = get_equipas()
    jogadores_lista = []
    equipa_selecionada = None
    equipa_nome = None
    
    if request.method == 'POST':
        id_equipa = request.form.get('id_equipa')
        if id_equipa:
            try:
                id_equipa = int(id_equipa)
                jogadores_lista = get_jogadores_por_equipa(id_equipa)
                equipa_selecionada = id_equipa
                equipa_nome = get_equipa_nome(id_equipa)
            except ValueError:
                flash("ID de equipa inválido", "error")
    
    return render_template('jogadores.html', 
                         equipas=equipas, 
                         jogadores=jogadores_lista,
                         equipa_selecionada=equipa_selecionada,
                         equipa_nome=equipa_nome)

@app.route('/add-jogador', methods=['GET', 'POST'])
def add_jogador():
    """Página para adicionar um novo jogador."""
    equipas = get_equipas()
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        posicao = request.form.get('posicao', '').strip()
        idade = request.form.get('idade', '')
        id_equipa = request.form.get('id_equipa', '')
        
        # Converter idade para inteiro se fornecida
        idade_int = None
        if idade:
            try:
                idade_int = int(idade)
            except ValueError:
                flash("Idade deve ser um número válido", "error")
                return render_template('add_jogador.html', equipas=equipas)
        
        # Converter id_equipa para inteiro
        try:
            id_equipa_int = int(id_equipa)
        except ValueError:
            flash("Equipa inválida", "error")
            return render_template('add_jogador.html', equipas=equipas)
        
        # Adicionar jogador
        sucesso, mensagem = adicionar_jogador(nome, posicao, idade_int, id_equipa_int)
        
        if sucesso:
            flash(mensagem, "success")
            return redirect(url_for('add_jogador'))
        else:
            flash(mensagem, "error")
    
    return render_template('add_jogador.html', equipas=equipas)

@app.errorhandler(404)
def not_found(error):
    """Trata erros 404."""
    return render_template('base.html', error="Página não encontrada"), 404

@app.errorhandler(500)
def server_error(error):
    """Trata erros 500."""
    return render_template('base.html', error="Erro interno do servidor"), 500

if __name__ == '__main__':
    # Inicializar a base de dados
    init_db()
    
    # Correr a aplicação
    app.run(debug=True, host='127.0.0.1', port=5000)
