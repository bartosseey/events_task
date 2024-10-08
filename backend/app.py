from flask import Flask
from flask_migrate import Migrate

from .config import Config
from .extensions import db, ma, jwt
from .auth.views import auth_bp
from .events.views import events_bp
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
ma.init_app(app)
jwt.init_app(app)
migrate = Migrate(app, db)
CORS(app, supports_credentials=True, origins="http://localhost:3000", allow_headers=["Authorization", "Content-Type"])

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(events_bp, url_prefix='/events')

if __name__ == '__main__':
    app.run(debug=True)
