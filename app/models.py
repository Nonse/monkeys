from app import db
from hashlib import md5
from sqlalchemy import func
from sqlalchemy.orm import aliased


friendship = db.Table('friendship',
    db.Column('monkey', db.Integer, db.ForeignKey('monkey.id')),
    db.Column('friend_of', db.Integer, db.ForeignKey('monkey.id'))
    )


class Monkey(db.Model):
    __tablename__ = 'monkey'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    age = db.Column(db.Integer, index=True)
    email = db.Column(db.String(100), index=True, unique=True)
    best_friend_id = db.Column(
        db.Integer,
        db.ForeignKey('monkey.id'),
        nullable=True
    )
    # Monkey can have one best friend but many monkeys can consider single
    # monkey as their best friend
    best_friend_of = db.relationship(
        'Monkey',
        backref=db.backref('best_friend', remote_side=[id]),
        lazy='dynamic'
    )
    friends = db.relationship(
        'Monkey',
        secondary=friendship,
        primaryjoin=(friendship.c.monkey == id),
        secondaryjoin=(friendship.c.friend_of == id),
        backref=db.backref('friends_of', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self): #this method is used for debugging
        return '<Monkey {}>'.format(self.name)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=retro&s=%d' % (md5(
            self.email.encode('utf-8')).hexdigest(), size
        )

    def is_friend(self, monkey):
        return self.friends.filter(
            friendship.c.friend_of == monkey.id
        ).count() > 0

    def add_friend(self, monkey):
        if self != monkey and not self.is_friend(monkey):
            self.friends.append(monkey)
            monkey.friends.append(self)
            return True
        else:
            return False

    def delete_friend(self, monkey):
        if self.is_friend(monkey):
            # to be best friends
            # monkeys must be at least friends
            if self.best_friend == monkey:
                self.best_friend = None
            self.friends.remove(monkey)
            monkey.delete_friend(self)
            return True
        else:
            return False

    def add_best_friend(self, monkey):
        if self != monkey and self.best_friend != monkey:
            if not self.is_friend(monkey):
                self.add_friend(monkey)
            self.best_friend = monkey
            return True
        else:
            return False

    def friends_without_best(self):
        if self.best_friend is not None:
            return self.friends.filter(Monkey.id != self.best_friend.id)
        else:
            return self.friends

    def non_friends(self):
        return Monkey.query.filter(
            Monkey.id != self.id
        ).except_all(self.friends)

    @staticmethod
    def query_with_friend_count():
        monkeys = Monkey.query.with_entities(
            Monkey,
            func.count(friendship.c.monkey).label('friend_count')
        ).outerjoin(
            friendship,
            Monkey.id==friendship.c.monkey
        ).group_by(Monkey)
        return monkeys

    @staticmethod
    def query_with_best_friend(bf_alias):
        monkeys = Monkey.query.with_entities(Monkey).outerjoin(
            bf_alias,
            Monkey.best_friend_id == bf_alias.id
        )
        return monkeys
