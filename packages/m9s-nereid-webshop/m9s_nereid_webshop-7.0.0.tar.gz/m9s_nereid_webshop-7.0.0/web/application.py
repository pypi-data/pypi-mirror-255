#!/usr/bin/env python
import os

from secure_cookie.session import FilesystemSessionStore

from trytond.config import config

from nereid import Nereid
from nereid.contrib.locale import Babel
from nereid.sessions import Session

config.update_etc()

CWD = os.path.abspath(os.path.dirname(__file__))

database_name = os.environ.get('DB_NAME')

CONFIG = dict(

    # The name of database
    DATABASE_NAME=database_name,

    # If the application is to be configured in the debug mode
    DEBUG=True,

    # The location where the translations of this template are stored
    TRANSLATIONS_PATH='i18n',

    # Secret Key: Replace this with something random
    # A good way to generate such a number would be
    #
    # >>> import os
    # >>> os.urandom(20)
    #
    SECRET_KEY='\xcd\x04}\x8d\\j-\x98b\xf2',

    CACHE_KEY_PREFIX=database_name,
)

# Create a new application
app = Nereid(static_folder='%s/static/' % CWD, static_url_path='/static')

# Update the configuration with the above config values
app.config.update(CONFIG)


# Initialise the app, connect to cache and backend
app.initialise()

# Setup the filesystem cache
app.session_interface.session_store = FilesystemSessionStore(
    '/tmp', session_class=Session
)

Babel(app)


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0')
