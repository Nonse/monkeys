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
