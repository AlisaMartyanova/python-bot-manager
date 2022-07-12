import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from app.resources.resources import UserRegistration
from app.resources.resources import UserLogin
from app.resources.resources import Bot
from app.resources.resources import BotStatus

app = Flask(__name__)
app.config.from_object('config.Config')
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


# adding end points
api.add_resource(UserRegistration, '/registration')
api.add_resource(UserLogin, '/login')
api.add_resource(Bot, '/bots')
api.add_resource(BotStatus, '/bots/status')

# configure jwt
jwt = JWTManager(app)

if __name__ == '__main__':
    from app.database import db
    db.init_app(app)

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
