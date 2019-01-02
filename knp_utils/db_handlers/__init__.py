#! -*- coding: utf-8 -*-
from knp_utils.logger_unit import logger
try:
    import leveldb
except ImportError:
    logger.error('leveldb package is not installed yet. To enable this module, please install leveldb package.')
else:
    from knp_utils.db_handlers import leveldb_handler
    from knp_utils.db_handlers.leveldb_handler import LevelDbHandler, LevelDB

from knp_utils.db_handlers.sqlite3_handler import Sqlite3Handler