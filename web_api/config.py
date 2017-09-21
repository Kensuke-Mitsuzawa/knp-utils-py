class BaseConfig(object):
    KNP_COMMAND = None
    JUMAN_COMMAND = None
    JUMANPP_COMMAND = None
    JUMANPP_SERVER_HOST = None
    JUMANPP_SERVER_PORT = None
    PATH_WORKING_DIR = None
    FILENAME_BACKEND_SQLITE3 = None
    # backend postgresql db #
    PSQL_HOST = None
    PSQL_PORT = None
    PSQL_USER = None
    PSQL_PASS = None
    PSQL_DB = None


class DevelopmentConfig(BaseConfig):
    KNP_COMMAND = "/usr/local/bin/knp"
    JUMAN_COMMAND = "/usr/local/bin/juman"
    JUMANPP_COMMAND = "/usr/local/bin/jumanpp"
    JUMANPP_SERVER_HOST = None
    JUMANPP_SERVER_PORT = None
    PATH_WORKING_DIR = './'
    FILENAME_BACKEND_SQLITE3 = 'backend.sqlite3'
    # backend postgresql db #
    PSQL_HOST = 'localhost'
    PSQL_PORT = 5432
    PSQL_USER = 'docker'
    PSQL_PASS = 'docker'
    PSQL_DB = 'backend_db'


class TestingConfig(BaseConfig):
    KNP_COMMAND = None
    JUMAN_COMMAND = None
    JUMANPP_SERVER_HOST = None
    JUMANPP_SERVER_PORT = None