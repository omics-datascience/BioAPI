import pytest
import os
import tempfile

import pytest
from flaskr import create_app
# from flaskr.db import get_db, init_db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    # with app.app_context():
    #     init_db()
    #     get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

