from flask import (
    Blueprint, render_template, request, flash,
    redirect, url_for, g, abort
)

from flaskr.db import get_db
from .auth import login_required

bp = Blueprint('blog', __name__, url_prefix='/blog')

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT *'
        ' FROM pet WHERE dono_id = ?'
        ' ORDER BY criado_em DESC',
        (g.user['id'],)
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        raca = request.form['raca']
        idade = request.form['idade']
        error = None

        if not nome:
            error = 'Nome é obrigatório.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO pet (nome, especie, raca, idade, dono_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (nome, especie, raca, idade, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT *'
        ' FROM pet'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Pet não encontrado.")

    if check_author and post['dono_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        raca = request.form['raca']
        idade = request.form['idade']
        error = None

        db = get_db()
        db.execute(
            'UPDATE pet SET nome = ?, especie = ?, raca = ?, idade = ?'
            ' WHERE id = ?',
            (nome, especie, raca, idade, id)
        )
        db.commit()
        return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM pet WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))