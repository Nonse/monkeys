#!venv/bin/python
import unittest
from app import app, db, models


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' #memory db
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestMonkey(TestCase):
    def test_friends(self):
        m1 = models.Monkey(name='monkey1', email='monkey1@example.com')
        m2 = models.Monkey(name='monkey2', email='monkey2@example.com')
        db.session.add_all([m1, m2])
        db.session.commit()

        assert m1.is_friend(m2) is False
        assert m2.is_friend(m1) is False
        assert m1.delete_friend(m2) is False
        assert m1.add_friend(m2) is True
        db.session.add_all([m1, m2])
        db.session.commit()

        assert m1.friends.count() == 1
        assert m2.friends.count() == 1
        assert m1.is_friend(m2) is True
        assert m2.is_friend(m1) is True
        assert m1.add_friend(m2) is False

        assert m1.delete_friend(m2) is True
        db.session.add_all([m1, m2])
        db.session.commit()
        assert m1.friends.count() == 0
        assert m2.friends.count() == 0
        assert m1.is_friend(m2) is False
        assert m2.is_friend(m1) is False

    def test_many_friends(self):
        m1 = models.Monkey(name='monkey1', email='monkey1@example.com')
        m2 = models.Monkey(name='monkey2', email='monkey2@example.com')
        m3 = models.Monkey(name='monkey3', email='monkey3@example.com')
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        assert m1.is_friend(m2) is False
        assert m1.is_friend(m3) is False
        assert m2.is_friend(m1) is False
        assert m2.is_friend(m3) is False
        assert m3.is_friend(m1) is False
        assert m3.is_friend(m2) is False
        assert m1.add_friend(m2) is True
        assert m1.add_friend(m3) is True
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        assert m1.friends.count() == 2
        assert m2.friends.count() == 1
        assert m3.friends.count() == 1
        assert m1.is_friend(m2) is True
        assert m1.is_friend(m3) is True
        assert m2.is_friend(m1) is True
        assert m2.is_friend(m3) is False
        assert m3.is_friend(m1) is True
        assert m3.is_friend(m2) is False
        assert m1.add_friend(m2) is False
        assert m1.add_friend(m3) is False

        assert m1.delete_friend(m2) is True
        assert m1.delete_friend(m3) is True
        db.session.add_all([m1, m2, m3])
        db.session.commit()
        assert m1.friends.count() == 0
        assert m2.friends.count() == 0
        assert m3.friends.count() == 0
        assert m1.is_friend(m2) is False
        assert m1.is_friend(m3) is False
        assert m2.is_friend(m1) is False
        assert m2.is_friend(m3) is False
        assert m3.is_friend(m1) is False
        assert m3.is_friend(m2) is False


if __name__ == '__main__':
    unittest.main()
