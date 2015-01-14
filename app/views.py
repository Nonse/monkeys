from flask import render_template, redirect, url_for, abort, flash, request
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import aliased
from app import app, db
from .forms import CreateMonkeyForm, EditMonkeyForm
from .models import Monkey, friendship


@app.route('/')
def index():
    friends = Monkey.query.all()
    return render_template('index.html',
                            friends=friends)


@app.route('/search', methods=['GET'])
def search ():
    friends = Monkey.query
    criteria = request.args.get('sort', '')
    if criteria == 'name_asc':
        friends = friends.order_by(asc(Monkey.name))
    elif criteria == 'name_desc':
        friends = friends.order_by(desc(Monkey.name))
    elif criteria.startswith('number_'):
        friends = db.session.query(
            Monkey,
            func.count(friendship.c.monkey).label('friend_count')
        ).outerjoin(
            friendship,
            Monkey.id==friendship.c.monkey
        ).group_by(Monkey)
        if criteria.endswith('asc'):
            friends = friends.order_by(asc('friend_count'))
        else:
            friends = friends.order_by(desc('friend_count'))
        friends = map(lambda f: f[0], friends)
    elif criteria.startswith('bf_'):
        bf_alias = aliased(Monkey)
        friends = db.session.query(Monkey).outerjoin(
            bf_alias,
            Monkey.best_friend_id == bf_alias.id
        )
        if criteria.endswith('asc'):
            friends = friends.order_by(asc(bf_alias.name))
        else:
            friends = friends.order_by(desc(bf_alias.name))
    return render_template('search.html',
                            friends=friends,
                            criteria=criteria)


@app.route('/monkey/<id>')
def profile(id, add_friends=False):
    monkey = Monkey.query.filter_by(id=id).scalar()
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
    monkey = Monkey.query.filter_by(id=id).scalar()
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
    monkey = Monkey.query.filter_by(id=id).scalar()
    db.session.delete(monkey)
    db.session.commit()
    flash('You just deleted ' + monkey.name)
    return redirect(url_for('index'))


@app.route('/add/<id>/<friend_id>')
def add_friend(id, friend_id):
    monkey = Monkey.query.filter_by(id=id).scalar()
    friend = Monkey.query.filter_by(id=friend_id).scalar()
    if monkey.add_friend(friend):
        db.session.add_all([monkey, friend])
        db.session.commit()
        flash('Friends with ' + friend.name)
    else:
        flash("Can't make friends with " + friend.name)
    return redirect(url_for('profile', id=monkey.id))


@app.route('/unfriend/<id>/<friend_id>')
def unfriend(id, friend_id):
    monkey = Monkey.query.filter_by(id=id).scalar()
    friend = Monkey.query.filter_by(id=friend_id).scalar()
    if monkey.delete_friend(friend):
        db.session.add_all([monkey, friend])
        db.session.commit()
        flash('Unfriended ' + friend.name)
    else:
        flash('Unfriending failed')
    return redirect(url_for('profile', id=monkey.id))


@app.route('/add_bf/<id>/<friend_id>')
def add_bf(id, friend_id):
    monkey = Monkey.query.filter_by(id=id).scalar()
    friend = Monkey.query.filter_by(id=friend_id).scalar()
    if monkey.add_best_friend(friend):
        db.session.add_all([monkey, friend])
        db.session.commit()
        flash("{} is now {}'s best friend".format(friend.name, monkey.name))
    else:
        flash('Failed to add {} as the best friend'.format(friend.name))
    return redirect(url_for('profile', id=monkey.id))


@app.route('/remove_bf/<id>')
def remove_bf(id):
    monkey = Monkey.query.filter_by(id=id).scalar()
    friend = monkey.best_friend
    monkey.best_friend = None
    db.session.add(monkey)
    db.session.commit()
    flash("{} is not {}'s best friend anymore".format(
        friend.name, monkey.name)
    )
    return redirect(url_for('profile', id=monkey.id))
