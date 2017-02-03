#! -*- coding: utf-8 -*-
import sys
import logging

custmoFormatter = logging.Formatter(
    fmt='[%(asctime)s]%(levelname)s - %(filename)s#%(funcName)s:%(lineno)d: %(message)s',
    datefmt='Y/%m/%d %H:%M:%S'
)

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(custmoFormatter)

logger_name = 'knp-utils'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
logger.addHandler(handler)