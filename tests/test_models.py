import random
from monkeygod import models


def test_avatar(session):
    """Gravatar URL should be generated"""
    m1 = models.Monkey(
        name='monkey1',
        age=10,
        email='monkey1@example.com'
    )
    session.add(m1)
    session.commit()
    avatar = m1.avatar(128)
    expected = (
        'http://www.gravatar.com/avatar/90cab8a06b72c3ea49d7a09192b43166'
        )
    assert avatar[0:len(expected)] == expected


def test_is_friend(session):
    m1 = models.Monkey(
        name='monkey1',
        age=10,
        email='monkey1@example.com'
    )
    m2 = models.Monkey(
        name='monkey2',
        age=20,
        email='monkey2@example.com'
    )
    m3 = models.Monkey(
        name='monkey3',
        age=30,
        email='monkey3@example.com'
    )
    session.add_all([m1, m2, m3])
    session.commit()
    m1.friends.append(m2)
    m2.friends.append(m1)
    session.add_all([m1, m2])
    session.commit()

    assert m1.is_friend(m2) is True
    assert m2.is_friend(m1) is True
    assert m2.is_friend(m3) is False
    assert m3.is_friend(m2) is False


def test_friends(session):
    """Database test to ensure a monkey can add/delete friends"""
    m1 = models.Monkey(
        name='monkey1',
        age=10,
        email='monkey1@example.com'
    )
    m2 = models.Monkey(
        name='monkey2',
        age=20,
        email='monkey2@example.com'
    )
    session.add_all([m1, m2])
    session.commit()

    assert m1.is_friend(m2) is False, 'Monkeys are not friends initially'
    assert m2.is_friend(m1) is False, 'Monkeys are not friends initially'
    assert m1.delete_friend(m2) is False, 'Removing non-existing friend fails'
    assert m1.add_friend(m1) is False, 'Cant add self to friends'
    assert m1.add_friend(m2) is True, 'Adding friend succeeds'
    session.add_all([m1, m2])
    session.commit()

    assert m1.friends.count() == 1, 'Monkey has 1 friend'
    assert m2.friends.count() == 1, 'Friendship is bidirectional'
    assert m1.is_friend(m2) is True, 'Friend is the correct one'
    assert m2.is_friend(m1) is True, 'Second monkey has the correct friend too'
    assert m1.add_friend(m2) is False, 'Cant add the existing friend'

    assert m1.delete_friend(m2) is True, 'Deleting friend works correctly'
    session.add_all([m1, m2])
    session.commit()
    assert m1.friends.count() == 0, 'Monkey again has no friends'
    assert m2.friends.count() == 0, 'Deleting friends is bidirectional'
    assert m1.is_friend(m2) is False, 'Monkeys are not friends anymore'
    assert m2.is_friend(m1) is False, 'Monkeys are not friends anymore'


def test_many_friends(session):
    """Database test to ensure a monkey can have more than one friend"""
    m1 = models.Monkey(
        name='monkey1',
        age=10,
        email='monkey1@example.com'
    )
    m2 = models.Monkey(
        name='monkey2',
        age=20,
        email='monkey2@example.com'
    )
    m3 = models.Monkey(
        name='monkey3',
        age=30,
        email='monkey3@example.com'
    )
    session.add_all([m1, m2, m3])
    session.commit()

    m1.add_friend(m2)
    assert m1.add_friend(m3) is True, 'Monkey can have more than 1 friend'
    session.add_all([m1, m2, m3])
    session.commit()

    assert m1.friends.count() == 2, 'Monkey1 have more than 1 friend'
    assert m2.friends.count() == 1, 'Friends added bidirectionally'
    assert m3.friends.count() == 1, 'Friends added bidirectionally'
    assert m2.is_friend(m3) is False, 'Two other monkeys are not friends'


def test_best_friends(session):
    """Database test to ensure best friend logic works correctly"""
    m1 = models.Monkey(
        name='monkey1',
        age=10,
        email='monkey1@example.com'
    )
    m2 = models.Monkey(
        name='monkey2',
        age=20,
        email='monkey2@example.com'
    )
    m3 = models.Monkey(
        name='monkey3',
        age=30,
        email='monkey3@example.com'
    )
    session.add_all([m1, m2, m3])
    session.commit()

    assert m1.best_friend is None, 'Monkey has no best friend initially'
    assert m2.best_friend is None, 'Monkey has no best friend initially'
    assert m3.best_friend is None, 'Monkey has no best friend initially'

    assert m1.add_best_friend(m1) is False, 'Cant add self as best friend'
    assert m1.add_best_friend(m3) is True, 'Can add other monkeys as bf'
    assert m2.add_best_friend(m3) is True, (
        'Multiple monkeys can consider one monkey best friend'
    )
    session.add_all([m1, m2, m3])
    session.commit()

    assert m1.best_friend == m3, 'Monkey has correct best friend'
    assert m3.best_friend_of.count() == 2, (
        'Monkey3 is considered best friend of multiple monkeys'
    )
    assert m3.best_friend is None, 'Best friend is not bidirectional'

    assert m1.add_best_friend(m2) is True, 'Can change best friend'
    m2.best_friend = None
    session.add_all([m1, m2, m3])
    session.commit()

    assert m1.best_friend == m2, 'Changed best friend successfully'
    assert m2.best_friend is None, 'Removing best friend succeeds'
    assert m1.delete_friend(m2) is True, 'Can delete friend who is also best'
    session.add_all([m1, m2, m3])
    session.commit()

    assert m1.best_friend is None, 'Deleting from friends also clears best'


def test_friends_without_best(session):
    m1 = models.Monkey(
        name='monkey1',
        age=10,
        email='monkey1@example.com'
    )
    m2 = models.Monkey(
        name='monkey2',
        age=20,
        email='monkey2@example.com'
    )
    m3 = models.Monkey(
        name='monkey3',
        age=30,
        email='monkey3@example.com'
    )
    session.add_all([m1, m2, m3])
    session.commit()
    m1.add_friend(m2)
    m1.add_best_friend(m3)
    session.add_all([m1, m2, m3])
    session.commit()

    no_bf_friends = m1.friends_without_best()
    for friend in no_bf_friends:
        assert m1.best_friend != friend
    assert (m1.friends.count() - no_bf_friends.count()) == 1, (
        'All friends but best'
    )
    assert m2.friends.count() == m2.friends_without_best().count(), (
        'Without best friend lists are the same'
    )


def test_non_friends(session):
    m1 = models.Monkey(
        name='monkey1',
        age=10,
        email='monkey1@example.com'
    )
    m2 = models.Monkey(
        name='monkey2',
        age=20,
        email='monkey2@example.com'
    )
    m3 = models.Monkey(
        name='monkey3',
        age=30,
        email='monkey3@example.com'
    )
    session.add_all([m1, m2, m3])
    session.commit()
    m1.add_friend(m2)
    session.add_all([m1, m2])
    session.commit()

    others = m1.non_friends()
    assert others.count() == 1, 'Lists one not added friend'

    for monkey in others:
        assert not m1.is_friend(monkey), 'Monkeys are not friends'
