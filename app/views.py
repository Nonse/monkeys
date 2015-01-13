from flask import render_template, redirect, url_for, abort, flash, request
from app import app, models
from .forms import CreateMonkeyForm, EditMonkeyForm
from .models import Monkey, db


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/monkey/<id>')
def profile(id, add_friends=False):
    monkey = models.Monkey.query.filter_by(id=id).scalar()
    if monkey == None:
       return abort(404)
    return render_template('profile.html',
                           monkey=monkey,
                           add_friends=add_friends)


@app.route('/monkey/<id>/add_friends')
def profile_add_friend(id):
    return profile(id, add_friends=True)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/create', methods=['GET', 'POST'])
def create_monkey():
    form = CreateMonkeyForm()
    if form.validate_on_submit():
        monkey = Monkey()
        monkey.name = form.name.data
        monkey.email = form.email.data
        db.session.add(monkey)
        db.session.commit()
        flash('Monkey created!')
        return redirect(url_for('profile', id=monkey.id))
    return render_template('create.html',
                            form=form)


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_monkey(id):
    form = EditMonkeyForm()
    monkey = models.Monkey.query.filter_by(id=id).scalar()
    if form.validate_on_submit():
        monkey.name = form.name.data
        monkey.email = form.email.data
        db.session.add(monkey)
        db.session.commit()
        flash('Monkey edited!')
        return redirect(url_for('profile', id=monkey.id))
    else:
        form.name.data = monkey.name
        form.email.data = monkey.email
    return render_template('edit.html',
                            form=form,
                            monkey=monkey)


@app.route('/delete/<id>')
def delete_monkey(id):
    monkey = models.Monkey.query.filter_by(id=id).scalar()
    db.session.delete(monkey)
    db.session.commit()
    flash('You just deleted ' + monkey.name)
    return redirect(url_for('index'))


@app.route('/add/<id>/<friend_id>')
def add_friend(id, friend_id):
    monkey = models.Monkey.query.filter_by(id=id).scalar()
    friend = models.Monkey.query.filter_by(id=friend_id).scalar()
    if monkey.add_friend(friend):
        db.session.add_all([monkey, friend])
        db.session.commit()
        flash('Friends with ' + friend.name)
    else:
        flash("Can't make friends with " + friend.name)
    return redirect(url_for('profile', id=monkey.id))


@app.route('/unfriend/<id>/<friend_id>')
def unfriend(id, friend_id):
    monkey = models.Monkey.query.filter_by(id=id).scalar()
    friend = models.Monkey.query.filter_by(id=friend_id).scalar()
    if monkey.delete_friend(friend):
        db.session.add_all([monkey, friend])
        db.session.commit()
        flash('Unfriended ' + friend.name)
    else:
        flash('Unfriending failed')
    return redirect(url_for('profile', id=monkey.id))
