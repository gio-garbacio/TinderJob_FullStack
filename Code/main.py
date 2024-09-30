from flask import Flask, render_template, redirect, url_for, session, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# Conexão com o banco de dados SQLite
def connect_db():
    conn = sqlite3.connect('devs_data.db')
    conn.row_factory = sqlite3.Row  
    return conn
# Criação das tabelas (se não existirem)
def create_tables():
    conn = connect_db()
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS developers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                cel TEXT NOT NULL,
                habilidades TEXT NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        conn.execute('''CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                cel TEXT NOT NULL,
                descricao TEXT NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        # Tabela para armazenar likes e dislikes dos devs
        conn.execute('''CREATE TABLE IF NOT EXISTS dev_likes (
                dev_id INTEGER NOT NULL,
                empresa_id INTEGER NOT NULL,
                action TEXT NOT NULL,  -- 'like' ou 'dislike'
                PRIMARY KEY (dev_id, empresa_id)
            )
        ''')
        # Tabela para armazenar likes e dislikes das empresas
        conn.execute('''CREATE TABLE IF NOT EXISTS empresa_likes (
                empresa_id INTEGER NOT NULL,
                dev_id INTEGER NOT NULL,
                action TEXT NOT NULL,  -- 'like' ou 'dislike'
                PRIMARY KEY (empresa_id, dev_id)
            )
        ''')
    conn.close()
create_tables()

# Formulários
class DevLoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')
class EmpresaLoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')
class DevForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    cel = StringField('Celular', validators=[DataRequired()])
    habilidades = TextAreaField('Habilidades', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')
class EmpresaForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    cel = StringField('Celular', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')   
class EditDevForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    cel = StringField('Celular', validators=[DataRequired()])
    habilidades = TextAreaField('Habilidades', validators=[DataRequired()])
    submit = SubmitField('Salvar Alterações')
class EditEmpresaForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    cel = StringField('Celular', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    submit = SubmitField('Salvar Alterações')


# INDEX ----------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# DEV LOGIN ------------------------------------------------------
@app.route("/dev/login", methods=["GET", "POST"])
def dev_login():
    form = DevLoginForm()
    if form.validate_on_submit():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM developers WHERE email = ? AND senha = ?", (form.email.data, form.senha.data))
        dev = cursor.fetchone()
        conn.close()
        if dev:
            session['dev_id'] = dev['id']
            return redirect(url_for('dev_home'))
        else:
            return render_template("dev_login.html", form=form, error="Email ou senha inválidos")
    return render_template("dev_login.html", form=form)

# DEV HOME -------------------------------------------------------
@app.route("/dev/home")
def dev_home():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empresas")
    empresas = cursor.fetchall() 
    conn.close()
    return render_template("dev_home.html", empresas=empresas)

# DEV REGISTRO ---------------------------------------------------
@app.route("/dev/register", methods=["GET", "POST"])
def dev_register():
    form = DevForm()
    if form.validate_on_submit():
        conn = connect_db()
        with conn:
            conn.execute('''
                INSERT INTO developers (name, email, cel, habilidades, senha)
                VALUES (?, ?, ?, ?, ?)
            ''', (form.name.data, form.email.data, form.cel.data, form.habilidades.data, form.senha.data))
        return redirect(url_for('home'))
    return render_template("dev_register.html", form=form)

# EMPRESA LOGIN --------------------------------------------------
@app.route("/empresa/login", methods=["GET", "POST"])
def empresa_login():
    form = EmpresaLoginForm()
    if form.validate_on_submit():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM empresas WHERE email = ? AND senha = ?", (form.email.data, form.senha.data))
        empresa = cursor.fetchone()
        conn.close()
        if empresa:
            session['empresa_id'] = empresa['id']
            return redirect(url_for('empresa_home'))
        else:
            return render_template("empresa_login.html", form=form, error="Email ou senha inválidos")
    return render_template("empresa_login.html", form=form)

# EMPRESA HOME ---------------------------------------------------
@app.route("/empresa/home")
def empresa_home():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM developers")
    developers = cursor.fetchall() 
    conn.close()
    return render_template("empresa_home.html", developers=developers)

# EMPRESA REGISTRO -----------------------------------------------
@app.route("/empresa/register", methods=["GET", "POST"])
def empresa_register():
    form = EmpresaForm()
    if form.validate_on_submit():
        conn = connect_db()
        with conn:
            conn.execute('''
                INSERT INTO empresas (name, email, cel, descricao, senha)
                VALUES (?, ?, ?, ?, ?)
            ''', (form.name.data, form.email.data, form.cel.data, form.descricao.data, form.senha.data))
        return redirect(url_for('home'))
    return render_template("empresa_register.html", form=form)

# DEV ACTION ----------------------------------------------------
@app.route("/dev/action/<int:empresa_id>/<action>")
def dev_action(empresa_id, action):
    dev_id = session.get('dev_id')  
    if not dev_id:
        return redirect(url_for('dev_login'))  
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO dev_likes (dev_id, empresa_id, action)
        VALUES (?, ?, ?)
    ''', (dev_id, empresa_id, action))
    cursor.execute('''
        SELECT action FROM empresa_likes
        WHERE empresa_id = ? AND dev_id = ? AND action = 'like'
    ''', (empresa_id, dev_id))
    empresa_like = cursor.fetchone()
    if action == 'like' and empresa_like:
        cursor.execute('''
            UPDATE dev_likes SET action = 'match' WHERE dev_id = ? AND empresa_id = ?
        ''', (dev_id, empresa_id))
        cursor.execute('''
            UPDATE empresa_likes SET action = 'match' WHERE empresa_id = ? AND dev_id = ?
        ''', (empresa_id, dev_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dev_home'))

# EMPRESA ACTION --------------------------------------------------
@app.route("/empresa/action/<int:dev_id>/<action>")
def empresa_action(dev_id, action):
    empresa_id = session.get('empresa_id') 
    if not empresa_id:
        return redirect(url_for('empresa_login'))  
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO empresa_likes (empresa_id, dev_id, action)
        VALUES (?, ?, ?)
    ''', (empresa_id, dev_id, action))
    cursor.execute('''
        SELECT action FROM dev_likes
        WHERE dev_id = ? AND empresa_id = ? AND action = 'like'
    ''', (dev_id, empresa_id))
    dev_like = cursor.fetchone()
    if action == 'like' and dev_like:
        cursor.execute('''
            UPDATE empresa_likes SET action = 'match' WHERE empresa_id = ? AND dev_id = ?
        ''', (empresa_id, dev_id))
        cursor.execute('''
            UPDATE dev_likes SET action = 'match' WHERE dev_id = ? AND empresa_id = ?
        ''', (dev_id, empresa_id))
    conn.commit()
    conn.close()
    return redirect(url_for('empresa_home'))

# DEV MATCHES ----------------------------------------------------
@app.route("/dev/matches")
def dev_matches():
    dev_id = session.get('dev_id')
    if not dev_id:
        return redirect(url_for('dev_login'))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.* FROM empresas e
        JOIN dev_likes dl ON e.id = dl.empresa_id
        JOIN empresa_likes el ON el.empresa_id = e.id AND el.dev_id = dl.dev_id
        WHERE dl.dev_id = ? AND dl.action = 'match' AND el.action = 'match'
    ''', (dev_id,))
    matches = cursor.fetchall()
    conn.close()
    return render_template("dev_matches.html", matches=matches)

# EMPRESA MATCHES -------------------------------------------------
@app.route("/empresa/matches")
def empresa_matches():
    empresa_id = session.get('empresa_id')
    if not empresa_id:
        return redirect(url_for('empresa_login'))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.* FROM developers d
        JOIN empresa_likes el ON d.id = el.dev_id
        JOIN dev_likes dl ON dl.dev_id = d.id AND dl.empresa_id = el.empresa_id
        WHERE el.empresa_id = ? AND el.action = 'match' AND dl.action = 'match'
    ''', (empresa_id,))
    matches = cursor.fetchall()
    conn.close()
    return render_template("empresa_matches.html", matches=matches)

# EDITAR PERFIL DEV ----------------------------------------------
@app.route("/dev/edit", methods=["GET", "POST"])
def edit_dev():
    dev_id = session.get('dev_id')
    if not dev_id:
        return redirect(url_for('dev_login'))
    form = EditDevForm()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM developers WHERE id = ?", (dev_id,))
    dev = cursor.fetchone()
    if request.method == 'GET':
        form.name.data = dev['name']
        form.email.data = dev['email']
        form.cel.data = dev['cel']
        form.habilidades.data = dev['habilidades']
    if form.validate_on_submit():
        with conn:
            conn.execute('''
                UPDATE developers SET name = ?, email = ?, cel = ?, habilidades = ?
                WHERE id = ?
            ''', (form.name.data, form.email.data, form.cel.data, form.habilidades.data, dev_id))
        conn.close()
        return redirect(url_for('dev_home'))
    conn.close()
    return render_template('edit_dev.html', form=form)

# EDITAR PERFIL EMPRESA--------------------------------------------
@app.route("/empresa/edit", methods=["GET", "POST"])
def edit_empresa():
    empresa_id = session.get('empresa_id')
    if not empresa_id:
        return redirect(url_for('empresa_login'))
    form = EditEmpresaForm()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empresas WHERE id = ?", (empresa_id,))
    empresa = cursor.fetchone()
    if request.method == 'GET':
        form.name.data = empresa['name']
        form.email.data = empresa['email']
        form.cel.data = empresa['cel']
        form.descricao.data = empresa['descricao']
    if form.validate_on_submit():
        with conn:
            conn.execute('''
                UPDATE empresas SET name = ?, email = ?, cel = ?, descricao = ?
                WHERE id = ?
            ''', (form.name.data, form.email.data, form.cel.data, form.descricao.data, empresa_id))
        conn.close()
        return redirect(url_for('empresa_home'))
    conn.close()
    return render_template('edit_empresa.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, port=6001)
