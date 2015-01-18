from flask import render_template, redirect, url_for, abort, flash, request
from sqlalchemy import asc, desc
from sqlalchemy.orm import aliased
from flask.ext.paginate import Pagination
from app import app, db
from .forms import CreateMonkeyForm, EditMonkeyForm
from .models import Monkey, friendship
from config import MONKEYS_PER_PAGE


@app.route('/')
def index():
    friends = Monkey.query.all()
    return render_template('index.html',
                            friends=friends)


@app.route('/search', methods=['GET'])
def search():
    monkey_query = Monkey.query
    criteria = request.args.get('sort', '')
    page = int(request.args.get('page', 1))
    pagination_query = None
    if criteria == 'name_asc':
        monkey_query = monkey_query.order_by(asc(Monkey.name))
    elif criteria == 'name_desc':
        monkey_query = monkey_query.order_by(desc(Monkey.name))
    elif criteria.startswith('number_'):
        monkey_query = Monkey.query_with_friend_count()
        if criteria.endswith('asc'):
            monkey_query = monkey_query.order_by(asc('friend_count'))
        else:
            monkey_query = monkey_query.order_by(desc('friend_count'))
        pagination_query = monkey_query.paginate(
            page,
            MONKEYS_PER_PAGE,
            False
        )
        monkeys = map(lambda f: f[0], pagination_query.items)
    elif criteria.startswith('bf_'):
        bf_alias = aliased(Monkey)
        monkey_query = Monkey.query_with_best_friend(bf_alias)
        if criteria.endswith('asc'):
            monkey_query = monkey_query.order_by(asc(bf_alias.name))
        else:
            monkey_query = monkey_query.order_by(desc(bf_alias.name))
    if not pagination_query:
        pagination_query = monkey_query.paginate(
            page,
            MONKEYS_PER_PAGE,
            False
        )
        monkeys = pagination_query.items
    pagination = Pagination(
        page=pagination_query.page,
        total=pagination_query.total,
        css_framework='bootstrap3'
    )
    return render_template('search.html',
                            monkeys=monkeys,
                            criteria=criteria,
                            pagination=pagination)


@app.route('/monkey/<id>')
def profile(id, add_friends=False):
    monkey = Monkey.query.filter_by(id=id).scalar()
    if monkey == None:
       return abort(404)
    page = int(request.args.get('page', 1))
    if add_friends:
        friends = monkey.non_friends()
        template = 'includes/add_friends.html'
    else:
        friends = monkey.friends_without_best()
        template = 'includes/friends.html'
    friends = friends.paginate(
            page,
            MONKEYS_PER_PAGE,
            False
        )
    pagination = Pagination(
        page=friends.page,
        total=friends.total,
        css_framework='bootstrap3'
    )
    return render_template('profile.html',
                           monkey=monkey,
                           friends=friends,
                           friends_template=template,
                           pagination=pagination)


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
        monkey.age = form.age.data
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
        monkey.age = form.age.data
        monkey.email = form.email.data
        db.session.add(monkey)
        db.session.commit()
        flash('Monkey edited!')
        return redirect(url_for('profile', id=monkey.id))
    else:
        form.name.data = monkey.name
        form.age.data = monkey.age
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
