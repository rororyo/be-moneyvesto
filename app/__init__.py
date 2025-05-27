import os
from flask import Flask
from dotenv import load_dotenv
from app.routes.user_routes import user_bp
from app.routes.transaction_routes import transaction_bp
from app.extensions import db,migrate
from flask_jwt_extended import JWTManager
jwt = JWTManager()

def create_app():
    load_dotenv()

    app = Flask(__name__)

    # database
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    dbname = os.getenv('DB_NAME')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    #init
    db.init_app(app)
    migrate.init_app(app,db=db)
    jwt.init_app(app)

    #Registering routes
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(transaction_bp, url_prefix='/api/transactions')

    with app.app_context():
        db.create_all()

    return app
