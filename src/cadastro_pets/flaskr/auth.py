import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        cpf = request.form['cpf']
        nome_dono = request.form['nome_dono']
        senha = request.form['senha']

        db = get_db()
        error = None

        if not cpf:
            error = 'CPF é obrigatório.'
        elif not nome_dono:
            error = 'Nome é obrigatório.'
        elif not senha:
            error = 'Senha é obrigatória.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO dono (cpf, nome_dono, senha) VALUES (?, ?, ?)",
                    (cpf, nome_dono, generate_password_hash(senha)),
                )
                db.commit()

            except db.IntegrityError:
                error = f"CPF {cpf} já foi cadastrado."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']

        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM dono WHERE cpf = ?',
            (cpf,)
        ).fetchone()

        if user is None:
            error = 'CPF incorreto.'
        elif not check_password_hash(user['senha'], senha):
            error = 'Senha incorreta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('auth.register_pet'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM dono WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/pet/register', methods=('GET', 'POST'))
@login_required
def register_pet():
    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        raca = request.form['raca']
        idade = request.form['idade']

        db = get_db()
        error = None

        dono_id = g.user['id']

        if not nome:
            error = 'Nome do pet é obrigatório.'
        elif not especie:
            error = 'Espécie é obrigatória.'

        if error is None:
            db.execute(
                'INSERT INTO pet (dono_id, nome, especie, raca, idade) VALUES (?, ?, ?, ?, ?)',
                (dono_id, nome, especie, raca, idade)
            )
            db.commit()

            return redirect(url_for('auth.register_pet'))
        
        flash(error)

    return render_template('pet/register.html')

