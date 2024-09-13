from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import NewTask, StatusEnum, User
from db import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id_usuario):
    return User.query.get(int(id_usuario))


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        NomeUsuario = request.form['nome_usuario']
        SenhaUsuario = request.form['senha_usuario']

        if User.query.filter_by(nome_usuario=NomeUsuario).first():
            flash('Nome de usuário já existente!')
            return redirect(url_for('registrar'))

        usuario = User(nome_usuario=NomeUsuario)
        usuario.definir_senha(SenhaUsuario)
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario)
        return redirect(url_for('all_tarefas'))
    return render_template('registroUsuario.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        NomeUsuario = request.form['nome_usuario']
        SenhaUsuario = request.form['senha_usuario']
        usuario = User.query.filter_by(nome_usuario=NomeUsuario).first()
        if usuario and usuario.checar_senha(SenhaUsuario):
            login_user(usuario)
            return redirect(url_for('all_tarefas'))
        else:
            flash('Usuário e/ou senha incorreto!', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/alltarefas')
@login_required
def all_tarefas():
    status_filter = request.args.get('status')

    query = NewTask.query.filter_by(user_id=current_user.id)

    if status_filter and status_filter in StatusEnum.__members__:
        query = query.filter_by(status=StatusEnum[status_filter])

    tarefas = query.all()

    return render_template('listar_tarefas.html', tarefas=tarefas, status_filter=status_filter)


@app.route('/novatarefa', methods=['GET', 'POST'])
@login_required
def nova_tarefa():
    if request.method == 'GET':
        return render_template('registrar_tarefa.html')
    elif request.method == 'POST':
        titulo = request.form['tituloForm']
        descricao = request.form['descricaoForm']
        status = request.form['statusForm']

        nova_tarefa = NewTask(
            titulo=titulo,
            descricao=descricao,
            status=status,
            user_id=current_user.id
        )

        db.session.add(nova_tarefa)
        db.session.commit()

        return redirect(url_for('all_tarefas'))


@app.route('/editartarefa/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(id):
    tarefa = NewTask.query.filter_by(id=id, user_id=current_user.id).first()
    if request.method == 'GET':
        if tarefa:
            return render_template('editar_tarefa.html', tarefa=tarefa)
        else:
            return render_template('erro.html', mensagem='Tarefa não encontrada'), 404
    elif request.method == 'POST':
        titulo = request.form['tituloForm']
        descricao = request.form['descricaoForm']
        status = request.form['statusForm']

        if tarefa:
            tarefa.titulo = titulo
            tarefa.descricao = descricao

            try:
                tarefa.status = StatusEnum[status]
            except KeyError:
                return render_template('erro.html', mensagem='Status inválido'), 400

            db.session.commit()
            return redirect(url_for('all_tarefas'))
        else:
            return render_template('erro.html', mensagem='Tarefa não encontrada'), 404


@app.route('/removertarefa/<int:id>', methods=['POST'])
@login_required
def remover_tarefa(id):
    tarefa = NewTask.query.filter_by(id=id, user_id=current_user.id).first()

    if tarefa:
        return redirect(url_for('confirmar_remocao', id=id))
    else:
        return render_template('erro.html', mensagem='Tarefa não encontrada'), 404


@app.route('/confirmarremocao/<int:id>', methods=['GET'])
@login_required
def confirmar_remocao(id):
    tarefa = NewTask.query.filter_by(id=id, user_id=current_user.id).first()

    if tarefa:
        return render_template('remover_tarefa.html', tarefa=tarefa)
    else:
        return render_template('erro.html', mensagem='Tarefa não encontrada'), 404


@app.route('/excluirtarefa/<int:id>', methods=['POST'])
@login_required
def excluir_tarefa(id):
    tarefa = NewTask.query.filter_by(id=id, user_id=current_user.id).first()
    if tarefa:
        db.session.delete(tarefa)
        db.session.commit()
        return redirect(url_for('all_tarefas'))
    else:
        return render_template('erro.html', mensagem='Tarefa não encontrada'), 404


@app.route('/dashboard')
def dashboard():
    # Consultar todas as tarefas
    tarefas = NewTask.query.all()
    return render_template('dashboard.html', tarefas=tarefas)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)
