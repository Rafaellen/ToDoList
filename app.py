from flask import Flask, render_template, redirect, request, url_for
from models import NewTask, StatusEnum
from db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
db.init_app(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/alltarefas')
def all_tarefas():
    # Obtém o filtro de status da URL
    status_filter = request.args.get('status')

    if status_filter and status_filter in StatusEnum.__members__:
        tarefas = NewTask.query.filter_by(
            status=StatusEnum[status_filter]).all()
    else:
        tarefas = NewTask.query.all()

    return render_template('listar_tarefas.html', tarefas=tarefas, status_filter=status_filter)


@app.route('/novatarefa', methods=['GET', 'POST'])
def nova_tarefa():
    if request.method == 'GET':
        return render_template('registrar_tarefa.html')
    elif request.method == 'POST':
        id = request.form['idForm']
        titulo = request.form['tituloForm']
        descricao = request.form['descricaoForm']
        status = request.form['statusForm']

        nova_tarefa = NewTask(id=id, titulo=titulo,
                              descricao=descricao, status=status)

        db.session.add(nova_tarefa)
        db.session.commit()

        return redirect(url_for('all_tarefas'))


@app.route('/editartarefa/<int:id>', methods=['GET', 'POST'])
def editar_tarefa(id):
    tarefa = db.session.query(NewTask).filter_by(id=id).first()
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
def remover_tarefa(id):
    tarefa = db.session.query(NewTask).filter_by(id=id).first()

    if tarefa:
        return redirect(url_for('confirmar_remocao', id=id))
    else:
        return render_template('erro.html', mensagem='Tarefa não encontrada'), 404


@app.route('/confirmarremocao/<int:id>', methods=['GET'])
def confirmar_remocao(id):
    tarefa = db.session.query(NewTask).filter_by(id=id).first()

    if tarefa:
        return render_template('remover_tarefa.html', tarefa=tarefa)
    else:
        return render_template('erro.html', mensagem='Tarefa não encontrada'), 404


@app.route('/excluirtarefa/<int:id>', methods=['POST'])
def excluir_tarefa(id):
    tarefa = db.session.query(NewTask).filter_by(id=id).first()
    if tarefa:
        db.session.delete(tarefa)
        db.session.commit()
        return redirect(url_for('all_tarefas'))
    else:
        return render_template('erro.html', mensagem='Tarefa não encontrada'), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)
