from flask import url_for
from monkeygod import models


def test_index(app):
    with app.test_client() as client:
        res = client.get(url_for('monkey_views.index'))
    assert 'Meet the Monkeys' in str(res.data)


def test_search_basic(app, testdata_with_friends):
    with app.test_client() as client:
        res = client.get(url_for('monkey_views.search'))
        assert res.status_code == 200, 'Search without parameters works'

        res = client.get(url_for('monkey_views.search', page=2))
        assert res.status_code == 200, 'Correct page works'

        res = client.get(url_for('monkey_views.search', page=10))
        assert res.status_code == 404, 'Wrong page gives 404'


def test_search_criteria(app, testdata_with_friends):
    criterias = [
        'name_asc', 'name_desc',
        'number_asc', 'number_desc',
        'bf_asc', 'bf_desc'
    ]
    with app.test_client() as client:
        for c in criterias:
            res = client.get(url_for('monkey_views.search', sort=c))
            assert res.status_code == 200, (
                'ORDER BY {}: Search without parameters works'.format(c)
            )

            res = client.get(url_for('monkey_views.search', sort=c, page=2))
            assert res.status_code == 200, (
                'ORDER BY {}: Correct page works'.format(c)
            )

            res = client.get(url_for('monkey_views.search', sort=c, page=10))
            assert res.status_code == 404, (
                'ORDER BY {}: Wrong page gives 404'.format(c)
            )


def test_profile(app, testdata_with_many_friends, session):
    with app.test_client() as client:
        monkey = models.Monkey.query.first()
        res = client.get(url_for('monkey_views.profile',
                                 id=monkey.id))
        assert res.status_code == 200, 'Correct view shown'
        res = client.get(url_for('monkey_views.profile',
                                 id=monkey.id, page=2))
        assert res.status_code == 200, 'Correct page works'
        res = client.get(url_for('monkey_views.profile',
                                 id=monkey.id, page=10))
        assert res.status_code == 404, 'Wrong page gives 404'


def test_profile_add_friend(app, testdata, session):
    with app.test_client() as client:
        monkey = models.Monkey.query.first()
        res = client.get(url_for('monkey_views.profile_add_friend',
                                 id=monkey.id))
        assert res.status_code == 200, 'Correct view shown'

        res = client.get(url_for('monkey_views.profile_add_friend',
                                 id=monkey.id, page=2))
        assert res.status_code == 200, 'Correct page works'
        res = client.get(url_for('monkey_views.profile_add_friend',
                                 id=monkey.id, page=10))
        assert res.status_code == 404, 'Wrong page gives 404'


def test_create_monkey(app, session):
    with app.test_client() as client:
        res = client.get(url_for('monkey_views.create_monkey'))
        assert res.status_code == 200, 'GET renders form'

        res = client.post(url_for('monkey_views.create_monkey'), data={
            'name': 'monkey',
            'age': '11',
            'email': 'monkey@example.com'
        })
        assert res.status_code == 302, 'Redirects correctly'
        assert models.Monkey.query.count() == 1, 'Monkey was created'
        monkey = models.Monkey.query.first()
        assert monkey.name == 'monkey'
        assert monkey.age == 11
        assert monkey.email == 'monkey@example.com'

        res = client.post(url_for('monkey_views.create_monkey'), data={
            'name': 'monkey',
            'email': 'monkey_email'
        })
        assert res.status_code == 200, 'Invalid data is shown'
        assert models.Monkey.query.count() == 1, (
            'Invalid monkey was not created'
        )


def test_edit_monkey(app, session):
    with app.test_client() as client:
        monkey = models.Monkey(
            name='monkey',
            age=11,
            email='monkey@example.com'
        )
        session.add(monkey)
        session.commit()
        res = client.get(url_for('monkey_views.edit_monkey', id=monkey.id))
        assert res.status_code == 200, 'GET renders form'

        res = client.post(
            url_for('monkey_views.edit_monkey', id=monkey.id),
            data={
                'name': 'monkey2',
                'age': '10',
                'email': 'monkey@example.fi'
            }
        )
        assert res.status_code == 302, 'Redirects correctly'
        assert monkey.name == 'monkey2'
        assert monkey.age == 10
        assert monkey.email == 'monkey@example.fi'

        res = client.post(
            url_for('monkey_views.edit_monkey', id=monkey.id),
            data={
                'name': 'monkey2',
                'email': 'monkey.fi'
            }
        )
        assert res.status_code == 200, 'Invalid data is shown'
        assert monkey.name == 'monkey2', 'Name not changed'
        assert monkey.age == 10, 'Age not changed'
        assert monkey.email == 'monkey@example.fi', 'Email not changed'


def test_delete_monkey(app, session):
    with app.test_client() as client:
        monkey = models.Monkey(
            name='monkey',
            age=11,
            email='monkey@example.com'
        )
        session.add(monkey)
        session.commit()
        res = client.get(url_for('monkey_views.delete_monkey', id=monkey.id))
        assert res.status_code == 302, 'Redirects correctly'
        assert models.Monkey.query.count() == 0, 'Monkey deleted successfully'


def test_add_friend(app, testdata, session):
    with app.test_client() as client:
        monkey1, monkey2 = models.Monkey.query[:2]

        res = client.get(url_for('monkey_views.add_friend',
                                 id=monkey1.id,
                                 friend_id=monkey2.id))
        assert res.status_code == 302, 'Redirects correctly'
        assert monkey1.is_friend(monkey2) is True, 'Monkeys are friends'


def test_unfriend(app, testdata, session):
    with app.test_client() as client:
        monkey1, monkey2 = models.Monkey.query[:2]
        monkey1.add_friend(monkey2)
        session.add_all([monkey1, monkey2])
        session.commit()

        res = client.get(url_for('monkey_views.unfriend',
                                 id=monkey1.id,
                                 friend_id=monkey2.id))
        assert res.status_code == 302, 'Redirects correctly'
        assert monkey1.is_friend(monkey2) is False, 'Monkeys are not friends'


def test_add_bf(app, testdata, session):
    with app.test_client() as client:
        monkey1, monkey2 = models.Monkey.query[:2]
        res = client.get(url_for('monkey_views.add_bf',
                                 id=monkey1.id,
                                 friend_id=monkey2.id))
        assert res.status_code == 302, 'Redirects correctly'
        assert monkey1.best_friend == monkey2, 'Monkeys are best friends'


def test_remove_bf(app, testdata, session):
    with app.test_client() as client:
        monkey1, monkey2 = models.Monkey.query[:2]
        monkey1.add_best_friend(monkey2)
        session.add_all([monkey1, monkey2])
        session.commit()
        res = client.get(url_for('monkey_views.remove_bf', id=monkey1.id))
        assert res.status_code == 302, 'Redirects correctly'
        assert monkey1.best_friend != monkey2, 'Monkeys are not best friends'
