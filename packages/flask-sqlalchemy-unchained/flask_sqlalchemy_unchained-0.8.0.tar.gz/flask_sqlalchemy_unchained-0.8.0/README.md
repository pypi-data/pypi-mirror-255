# Flask SQLAlchemy Unchained

Integrates [SQLAlchemy Unchained](https://github.com/briancappello/sqlalchemy-unchained) with [Flask](http://flask.pocoo.org/). This package is a very thin wrapper around [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org), and in terms of registering the extension with Flask, everything is the same.

## Basic Usage

```python
# your_app.py

from flask import Flask
from flask_sqlalchemy_unchained import SQLAlchemyUnchained


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemyUnchained(app)


class User(db.Model):
    class Meta:
        repr = ('id', 'username', 'email')

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
```

Now let's create the table and add a row:

```bash
export FLASK_APP='./your_app.py'
export FLASK_DEBUG='true'
flask shell
```

```
>>> from your_app import db, User
>>> db.create_all()
>>> user = User(username='fooar', email='foo@bar.com')
>>> db.session.add(user)
>>> db.session.commit()
>>> assert User.query.all() == [user]
```

## Real-World Usage

Now let's take a look at using the application factory pattern. Our app's directory structure will look like this:

```
./your-project
├── app
│   ├── models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── model_manager.py
│   │   └── user_manager.py
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   └── factory.py
├── db
│   └── dev.sqlite
├── tests
│   ├── __init__.py
│   └── test_user.py
├── autoapp.py
└── setup.py
```

The entry point of our app will be `autoapp.py`, so let's take a look at that first:

```python
# app/autoapp.py

import os

from app.factory import create_app


app = create_app(os.getenv('FLASK_ENV', 'development'))
```

And now the app factory:

```python
# app/factory.py
from flask import Flask

from .config import DevConfig, ProdConfig, TestConfig
from .extensions import db


CONFIGS = {
    'development': DevConfig,
    'production': ProdConfig,
    'test': TestConfig,
}


def create_app(env):
    config = CONFIGS[env]

    app = Flask(__name__,
                template_folder=config.TEMPLATE_FOLDER,
                static_folder=config.STATIC_FOLDER,
                static_url_path=config.STATIC_URL_PATH)
    app.config.from_object(config)

    db.init_app(app)

    return app
```

Which leads us to the `config` and `extensions` modules:

```python
# app/config.py

import os


class BaseConfig:
    DEBUG = os.getenv('FLASK_DEBUG', False)

    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(BaseConfig):
    DEBUG = os.getenv('FLASK_DEBUG', True)

    db_path = os.path.join(BaseConfig.PROJECT_ROOT, 'db', 'dev.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_path


class ProdConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = \
        '{engine}://{user}:{password}@{host}:{port}/{db_name}'.format(
            engine='postgresql+psycopg2',
            user=os.getenv('FLASK_DATABASE_USER', 'sqlalchemy_demo'),
            password=os.getenv('FLASK_DATABASE_PASSWORD', 'sqlalchemy_demo'),
            host=os.getenv('FLASK_DATABASE_HOST', '127.0.0.1'),
            port=os.getenv('FLASK_DATABASE_PORT', 5432),
            db_name=os.getenv('FLASK_DATABASE_NAME', 'sqlalchemy_demo'))


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # :memory:
```

```python
# app/extensions.py

from flask_sqlalchemy_unchained import SQLAlchemyUnchained


db = SQLAlchemyUnchained()
```

The `User` model is the same as before:

```python
# app/models/user.py

from app.extensions import db


class User(db.Model):
    class Meta:
        repr = ('id', 'username', 'email')

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
```

Because SQLAlchemy uses the data-mapper pattern, it's best practice to use managers/services for dealing with interactions with the database. A good base to start from might look like this:

```python
# app/services/model_manager.py

from typing import *

from app.extensions import db


class ModelManager:
    model: Type[db.Model]

    def create(self, commit: bool = False, **kwargs) -> db.Model:
        instance = self.model(**kwargs)
        self.save(instance, commit)
        return instance

    def update(self, instance: db.Model, commit: bool = False,
               **kwargs) -> db.Model:
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        self.save(instance, commit)
        return instance

    def delete(self, instance: db.Model, commit: bool = False) -> None:
        db.session.delete(instance)
        if commit:
            self.commit()

    def save(self, instance: db.Model, commit: bool = True):
        db.session.add(instance)
        if commit:
            self.commit()

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()

    def get(self, id) -> db.Model:
        return db.session.get(self.model, id)

    def get_by(self, **kwargs) -> db.Model:
        return db.session.query(self.model).filter_by(**kwargs).first()

    def find_all(self) -> List[db.Model]:
        return db.session.query(self.model).all()

    def find_by(self, **kwargs) -> List[db.Model]:
        return db.session.query(self.model).filter_by(**kwargs).all()
```

And then the `UserManager` class would look like this:

```python
# app/services/user_manager.py

from ..models import User

from .model_manager import ModelManager


class UserManager(ModelManager):
    model = User

    def create(self, username, email, **kwargs) -> User:
        return super().create(username=username, email=email, **kwargs)


user_manager = UserManager()
```

The full source code for this example app, including integrations with [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) and [Py-YAML-Fixtures](https://py-yaml-fixtures.readthedocs.io/en/latest/), can be found [on GitHub](https://github.com/briancappello/sqlalchemy-demo).
