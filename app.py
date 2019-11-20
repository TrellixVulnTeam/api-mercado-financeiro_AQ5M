from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import pandas_datareader.data as web
from pandas_datareader.data import YahooOptions
from flask import jsonify

app = Flask(__name__)

# Cria o banco de dados
# app.config['SQLAlCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

# Inicializa o banco
db = SQLAlchemy(app)


# classe que modela o banco
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id # retorna o id da tarefa


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'erro ao salvar no banco'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Erro ao deletar tarefa'


@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Erro ao atualizar a tarefa'
    else:
        return render_template('update.html', task=task)


@app.route('/lista')
def lista():
    start = datetime(2015, 1, 1)
    end = datetime(2015, 12, 1)
    facebook = web.DataReader('FB', 'yahoo', start, end)
    stocks = pd.DataFrame(facebook)
    data = []
    
    for info in range(0, len(stocks)):
        # data.append({'high': stocks['High'][info], 'low': stocks['Low'][info], 'open': stocks['Open'][info], 'close': stocks['Close'][info], 'volume': stocks['Volume'][info], 'adj_close': stocks['Adj Close'][info]})
        data.append({'high': stocks['High'][info], 'low': stocks['Low'][info], 'open': stocks['Open'][info], 'close': stocks['Close'][info], 'volume': stocks['Volume'][info]/100, 'adj_close': stocks['Adj Close'][info]})
    
    print(data)
    return jsonify(data)
    # return render_template('data.html', data=stocks)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)