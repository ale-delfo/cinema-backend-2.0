from flask_httpauth import HTTPTokenAuth
import firebase_admin
from firebase_admin import auth, credentials
import configparser

config = configparser.ConfigParser()
config.read('./config/basic_config.ini')
environment = config['GENERAL']['environment']

if environment not in ['local', 'production']:
    raise Exception('Error in environment configuration, please check basic_config.ini')


# ----------------------------------------
# Token authentication stuff
# ________________________________________

authorization = HTTPTokenAuth(scheme='Bearer')


if environment == 'production':
    cred = credentials.Certificate("config/cinema-food-firebase-adminsdk-dskp9-98ba81129d.json")
    firebase_admin.initialize_app(cred)

    @authorization.verify_token
    def verify_token(token):
        """
        The function set the method to be used for token authentication by the Flask-HTTPAuth module
        Reads the token and pass it to the verify_id_token function of the Firebase SDK
        """
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token['uid']
        except auth.InvalidIdTokenError:
            return False

if environment == 'local':
    @authorization.verify_token
    def verify_token(token):
        return token
