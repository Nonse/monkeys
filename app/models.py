from app import db


friendship = db.Table('friendship',
    db.Column('monkey', db.Integer, db.ForeignKey('monkey.id')),
    db.Column('friend_of', db.Integer, db.ForeignKey('monkey.id'))
    )


class Monkey(db.Model):
    __tablename__ = 'monkey'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
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
        return '<Monkey %r>' % (self.name)

    def is_friend(self, monkey):
        return self.friends.filter(
            friendship.c.friend_of == monkey.id
        ).count() > 0

    def add_friend(self, monkey):
        if not self.is_friend(monkey):
            self.friends.append(monkey)
            monkey.friends.append(self)
            return True
        else:
            return False

    def delete_friend(self, monkey):
        if self.is_friend(monkey):
            self.friends.remove(monkey)
            monkey.friends.remove(self)
            return True
        else:
            return False
