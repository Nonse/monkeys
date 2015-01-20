import os
import pytest
import random
import config
from monkeygod import create_app, models
from monkeygod.models import db as _db


TEST_DATABASE_URI = 'sqlite://'


# Adapted from http://goo.gl/KXDq2p
@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    config.TESTING = True
    config.SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URI
    config.CSRF_ENABLED = False
    config.WTF_CSRF_ENABLED = False
    app = create_app(config)

    # Establish an application context before running the tests.
    context = app.app_context()
    context.push()

    def teardown():
        context.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def testdata(session, request):
    monkeys = []
    for i in range(20):
        monkeys.append(
            models.Monkey(
                name='monkey{}'.format(i+1),
                age=random.randint(0, 20),
                email='monkey{}@example.com'.format(i+1)
            )
        )
    session.add_all(monkeys)
    session.commit()

    def teardown():
        for monkey in monkeys:
            session.delete(monkey)
        session.commit()

    request.addfinalizer(teardown)


@pytest.fixture(scope='function')
def testdata_with_friends(session, testdata, request):
    monkeys = models.Monkey.query.all()

    for monkey in monkeys:
        friends = random.sample(monkeys, random.randint(0, 20))
        for friend in friends:
            if random.randint(0, 5) == 0:
                monkey.add_best_friend(friend)
            else:
                monkey.add_friend(friend)

    session.add_all(monkeys)
    session.commit()
