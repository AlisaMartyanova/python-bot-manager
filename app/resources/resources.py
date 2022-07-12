from flask_restful import Resource
from flask_restful import reqparse
from datetime import timedelta
from app import bot
from app.models import models
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

help_message = 'This field cannot be blank'

auth_parser = reqparse.RequestParser()
auth_parser.add_argument('username', help=help_message, required=True)
auth_parser.add_argument('password', help=help_message, required=True)

token_parser = reqparse.RequestParser()
token_parser.add_argument('token', help=help_message, required=True)

status_parser = reqparse.RequestParser()
status_parser.add_argument('status', help=help_message, required=True)


def get_cur_user(username):
    return models.UserModel.find_by_username(username)


def check_bot_existence(current_user, token):
    if not models.BotModel.find_by_token(token):
        return {'message': 'No such bot'}, 404
    elif models.BotModel.find_by_token(token).user_id != current_user.id:
        return {'message': 'Access denied'}, 403


class UserRegistration(Resource):
    def post(self):
        data = auth_parser.parse_args()
        access_token_expiration_time = timedelta(minutes=60)
        refresh_token_expiration_time = timedelta(days=1)

        if models.UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}, 409

        new_user = models.UserModel(
            username=data['username'],
            password=models.UserModel.generate_hash(data['password'])
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['username'], expires_delta=access_token_expiration_time)
            refresh_token = create_refresh_token(identity=data['username'], expires_delta=refresh_token_expiration_time)
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 201
        except Exception as e:
            print(str(e))
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = auth_parser.parse_args()
        access_token_expiration_time = timedelta(minutes=60)
        refresh_token_expiration_time = timedelta(days=1)
        current_user = get_cur_user(data['username'])

        if not current_user:
            return {'message': 'User {} does not exist'.format(data['username'])}, 401

        if models.UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'], expires_delta=access_token_expiration_time)
            refresh_token = create_refresh_token(identity=data['username'], expires_delta=refresh_token_expiration_time)
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
                }, 200
        else:
            return {'message': 'Wrong credentials'}, 401


class Bot(Resource):
    @jwt_required()
    def get(self):
        current_user = get_cur_user(get_jwt_identity())

        def to_json(x):
            return {
                'user_id': x.user_id,
                'token': x.token,
                'status': x.status
            }

        return {
            "username": current_user.username,
            "bots": list(
                map(lambda x: to_json(x), models.BotModel.find_by_userid(current_user.id))
            )
        }, 200

    @jwt_required()
    def post(self):
        current_user = get_cur_user(get_jwt_identity())
        token = token_parser.parse_args()["token"]

        if models.BotModel.find_by_token(token):
            return {'message': 'This bot already exists'}
        if len(models.BotModel.find_by_userid(current_user.id)) >= 5:
            return {'message': 'Limit of bots is exceeded'}

        new_bot = models.BotModel(
            token=token,
            user_id=current_user.id,
            status=True
        )
        try:
            bot.start(token)
            new_bot.save_to_db()
        except Exception as e:
            print(str(e))
            return {'message': 'Something went wrong. Bot was not created'}, 500

        return {'message': 'Bot was successfully created'}, 200

    @jwt_required()
    def delete(self):
        current_user = get_cur_user(get_jwt_identity())
        token = token_parser.parse_args()["token"]

        mes = check_bot_existence(current_user, token)
        if mes: return mes

        try:
            bot.stop(token)
            models.BotModel.delete_by_token(current_user.id, token)
        except Exception as e:
            print(str(e))
            return {'message': 'Something went wrong. Bot was not deleted.'}, 500

        return {'message' : 'Bot successfully deleted'}, 200


class BotStatus(Resource):
    @jwt_required()
    def get(self):
        current_user = get_cur_user(get_jwt_identity())
        token = token_parser.parse_args()["token"]

        mes = check_bot_existence(current_user, token)
        if mes: return mes

        try:
            status = models.BotModel.get_bot_status(current_user.id, token)

            return {
                "username": current_user.username,
                "bot status": status
            }, 200
        except Exception as e:
            print(str(e))
            return {'message': 'Something went wrong'}, 500

    @jwt_required()
    def put(self):
        current_user = get_cur_user(get_jwt_identity())
        token = token_parser.parse_args()["token"]
        status = status_parser.parse_args()["status"].lower() == "true"

        mes = check_bot_existence(current_user, token)
        if mes: return mes

        try:
            bot.start(token) if status else bot.stop(token)
            models.BotModel.change_bot_status(current_user.id, token, status)
        except Exception as e:
            print(str(e))
            return {'message': 'Something went wrong. Bot status has not been changed.'}, 500

        return {"message": "Bot status was successfully changed"}, 200
