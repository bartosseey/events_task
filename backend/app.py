from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .config import Config
from .db import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

if __name__ == '__main__':
    app.run(debug=True)
