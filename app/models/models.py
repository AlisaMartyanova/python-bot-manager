from passlib.hash import pbkdf2_sha256 as sha256
from app.database import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }

        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class BotModel(db.Model):
    __tablename__ = 'bots'

    token = db.Column(db.Text, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Boolean, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_userid(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def find_by_token(cls, token):
        return cls.query.filter_by(token=token).first()

    @classmethod
    def delete_by_token(cls, user_id, token):
        bot = cls.query.filter_by(user_id=user_id, token = token).first()
        db.session.delete(bot)
        db.session.commit()

    @classmethod
    def get_bot_status(cls, user_id, token):
        return cls.query.filter_by(user_id=user_id, token = token).first().status

    @classmethod
    def change_bot_status(cls, user_id, token, status):
        bot = cls.query.filter_by(user_id=user_id, token = token).first()
        bot.status = status
        db.session.commit()
