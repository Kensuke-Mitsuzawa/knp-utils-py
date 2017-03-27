class BaseConfig(object):
    KNP_COMMAND = None
    JUMAN_COMMAND = None
    JUMANPP_SERVER_HOST = None
    JUMANPP_SERVER_PORT = None
    PATH_WORKING_DIR = None
    FILENAME_BACKEND_SQLITE3 = None


class DevelopmentConfig(BaseConfig):
    KNP_COMMAND = "/usr/local/bin/knp"
    JUMAN_COMMAND = "/usr/local/bin/juman"
    # todo juman++サーバーを複数threadから要求すると、落ちる
    JUMANPP_SERVER_HOST = None
    JUMANPP_SERVER_PORT = None
    PATH_WORKING_DIR = './'
    FILENAME_BACKEND_SQLITE3 = 'backend.sqlite3'


class TestingConfig(BaseConfig):
    KNP_COMMAND = None
    JUMAN_COMMAND = None
    JUMANPP_SERVER_HOST = None
    JUMANPP_SERVER_PORT = None