from flask import Flask
from flask_migrate import Migrate

from ammonia.db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/ammonia?charset=utf8'

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
