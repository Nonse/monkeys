from flask import render_template, redirect, url_for, abort, flash, request
from app import app, models
from .forms import CreateMonkeyForm
from .models import Monkey, db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/monkey/<id>')
def profile(id):
    monkey = models.Monkey.query.filter_by(id=id).scalar()
    if monkey == None:
       return abort(404)
    return render_template('profile.html',
                           monkey=monkey)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/create', methods=['GET', 'POST'])
def create_monkey():
    form = CreateMonkeyForm()
    if request.method == 'POST':
        monkey = Monkey()
        monkey.name = form.name.data
        monkey.email = form.email.data
        db.session.add(monkey)
        db.session.commit()
        flash('Monkey created!')
        return redirect(url_for('profile', id=monkey.id))
    else:
        form.name.data = 'name'
        form.email.data = 'email'
    return render_template('create.html',
                            form=form)

@app.route('/delete/monkey/<id>/<friend_id>')
def unfriend(id, friend_id):
    monkey = models.Monkey.query.filter_by(id=id).scalar()
    friend = models.Monkey.query.filter_by(id=friend_id).scalar()
    if monkey.delete_friend(friend):
        db.session.add_all([monkey, friend])
        db.session.commit()
        flash('You unfriended ' + friend.name)
    else:
        flash('Nope')
    return redirect(url_for('profile', id=monkey.id))
