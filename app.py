from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'futebol.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'base de dados')


def get_db_connection():
    """Cria uma conexão à base de dados com row factory ativado."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def seed_sample_data(conn):
    """Insere dados de exemplo para facilitar testes da aplicação."""
    cursor = conn.cursor()
    total_equipas = cursor.execute('SELECT COUNT(*) FROM equipa').fetchone()[0]

    if total_equipas == 0:
        cursor.executescript(
            """
            INSERT INTO equipa (nome, cidade, treinador) VALUES
            ('Sporting CP', 'Lisboa', 'Rúben Amorim'),
            ('SL Benfica', 'Lisboa', 'Bruno Lage'),
            ('FC Porto', 'Porto', 'Martín Anselmi'),
            ('SC Braga', 'Braga', 'Carlos Carvalhal');

            INSERT INTO jogador (nome, posicao, idade, id_equipa) VALUES
            ('Pedro Gonçalves', 'Médio', 26, 1),
            ('Ángel Di María', 'Avançado', 37, 2),
            ('Diogo Costa', 'Guarda-redes', 25, 3),
            ('Ricardo Horta', 'Avançado', 30, 4);
            """
        )


def init_db():
    """Inicializa a base de dados com o esquema presente no repositório."""
    if os.path.exists(DATABASE):
        return

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as schema_file:
        schema_sql = schema_file.read()

    conn = get_db_connection()
    try:
        conn.executescript(schema_sql)
        seed_sample_data(conn)
        conn.commit()
    finally:
        conn.close()


def get_equipas():
    """Obtém a lista de todas as equipas."""
    conn = get_db_connection()
    try:
        return conn.execute('SELECT id_equipa, nome FROM equipa ORDER BY nome').fetchall()
    finally:
        conn.close()


def get_jogadores_por_equipa(id_equipa):
    """Obtém todos os jogadores de uma equipa específica."""
    conn = get_db_connection()
    try:
        return conn.execute(
            'SELECT id_jogador, nome, posicao, idade FROM jogador WHERE id_equipa = ? ORDER BY nome',
            (id_equipa,),
        ).fetchall()
    finally:
        conn.close()


def get_equipa_nome(id_equipa):
    """Obtém o nome da equipa pelo ID."""
    conn = get_db_connection()
    try:
        equipa = conn.execute('SELECT nome FROM equipa WHERE id_equipa = ?', (id_equipa,)).fetchone()
        return equipa['nome'] if equipa else None
    finally:
        conn.close()


def adicionar_jogador(nome, posicao, idade, id_equipa):
    """Adiciona um novo jogador à base de dados."""
    if not nome or not id_equipa:
        return False, 'Nome e Equipa são obrigatórios'

    if idade is not None and (idade < 16 or idade > 50):
        return False, 'Idade deve estar entre 16 e 50 anos'

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO jogador (nome, posicao, idade, id_equipa) VALUES (?, ?, ?, ?)',
            (nome, posicao or None, idade, id_equipa),
        )
        conn.commit()
        return True, 'Jogador adicionado com sucesso!'
    except sqlite3.IntegrityError:
        return False, 'Erro: dados inválidos'
    finally:
        conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/jogadores', methods=['GET', 'POST'])
def jogadores():
    equipas = get_equipas()
    jogadores_lista = []
    equipa_selecionada = None
    equipa_nome = None

    if request.method == 'POST':
        id_equipa = request.form.get('id_equipa', '').strip()
        if not id_equipa:
            flash('Seleciona uma equipa.', 'warning')
        else:
            try:
                equipa_selecionada = int(id_equipa)
                equipa_nome = get_equipa_nome(equipa_selecionada)
                if equipa_nome is None:
                    flash('Equipa inválida.', 'danger')
                    equipa_selecionada = None
                else:
                    jogadores_lista = get_jogadores_por_equipa(equipa_selecionada)
            except ValueError:
                flash('ID de equipa inválido.', 'danger')

    return render_template(
        'jogadores.html',
        equipas=equipas,
        jogadores=jogadores_lista,
        equipa_selecionada=equipa_selecionada,
        equipa_nome=equipa_nome,
    )


@app.route('/add-jogador', methods=['GET', 'POST'])
def add_jogador():
    equipas = get_equipas()

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        posicao = request.form.get('posicao', '').strip()
        idade_raw = request.form.get('idade', '').strip()
        id_equipa_raw = request.form.get('id_equipa', '').strip()

        idade = None
        if idade_raw:
            try:
                idade = int(idade_raw)
            except ValueError:
                flash('Idade deve ser um número válido.', 'danger')
                return render_template('add_jogador.html', equipas=equipas)

        try:
            id_equipa = int(id_equipa_raw)
        except ValueError:
            flash('Seleciona uma equipa válida.', 'danger')
            return render_template('add_jogador.html', equipas=equipas)

        sucesso, mensagem = adicionar_jogador(nome, posicao, idade, id_equipa)
        flash(mensagem, 'success' if sucesso else 'danger')
        if sucesso:
            return redirect(url_for('add_jogador'))

    return render_template('add_jogador.html', equipas=equipas)


@app.errorhandler(404)
def not_found(error):
    return render_template('index.html', error='Página não encontrada'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('index.html', error='Erro interno do servidor'), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
