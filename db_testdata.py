#!venv/bin/python
from app import db, models


def clear_db():
    monkeys = models.Monkey.query.all()
    for m in monkeys:
        db.session.delete(m)

    db.session.commit()


def insert_data():
    m1 = models.Monkey(name='monkey1', email='monkey1@example.com')
    m2 = models.Monkey(name='monkey2', email='monkey2@example.com')
    m3 = models.Monkey(name='monkey3', email='monkey3@example.com')
    m4 = models.Monkey(name='monkey4', email='monkey4@example.com')
    m5 = models.Monkey(name='monkey5', email='monkey5@example.com')
    m6 = models.Monkey(name='monkey6', email='monkey6@example.com')

    db.session.add_all([m1, m2, m3, m4, m5, m6])
    db.session.commit()

    m1.add_friend(m2)
    m3.add_friend(m4)
    m5.add_friend(m6)

    db.session.add_all([m1, m2, m3, m4, m5, m6])
    db.session.commit()


if __name__ == '__main__':
    print('Clearing data..')
    clear_db()
    print('Inserting test data..')
    insert_data()
    print('Done')
