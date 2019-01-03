#! -*- coding: utf-8 -*-
# package modules
from knp_utils import logger_unit
from knp_utils.models import DocumentObject
from knp_utils.db_handlers.base import DbHandler
from six import text_type, PY2, PY3
# typing
from typing import List, Union, Iterable, Optional
# else
import json
import os
import traceback
import sqlite3
import six
import time
import random
import zlib
logger = logger_unit.logger

TIME_SLEEP = random.randint(2, 10)
N_RETRY = 60



class Sqlite3Handler(DbHandler):
    """Class object of backend DB handler in this package. The class uses sqlite3.
    """
    def __init__(self,
                 path_sqlite_file,
                 table_name_text="text",
                 is_close_connection_end=True,
                 sleep_time=TIME_SLEEP,
                 n_retry=N_RETRY,
                 connection_timeout=30000,
                 is_compress=True):
        # type: (str,str,bool,int,int,int,bool)->None
        """
        :param is_close_connection_end: If True, it deleted DB when a process is done. False; don't.
        :param sleep_time: time(seconds) to wait when it has database lock error from sqlite3
        :param n_retry: times to try and wait for database lock from sqlite3
        :param connection_timeout: timeout time until a connection will be closed.
        :param is_compress: boolean flag True; compress knp parsed result with zip.
        """
        self.is_compress = is_compress
        self.table_name_text = table_name_text
        self.is_close_connection_end = is_close_connection_end
        self.path_sqlite_file = path_sqlite_file
        self.sleep_time = sleep_time
        self.n_retry = n_retry
        self.connection_timeout = connection_timeout
        if not os.path.exists(self.path_sqlite_file):
            self.db_connection = sqlite3.connect(database=self.path_sqlite_file, isolation_level=None, timeout=self.connection_timeout)
            self.db_connection.text_factory = str
            self.create_db()
        else:
            self.db_connection = sqlite3.connect(database=self.path_sqlite_file, isolation_level=None, timeout=self.connection_timeout)
            self.db_connection.text_factory = str

    def __del__(self):
        if self.is_close_connection_end and hasattr(self, 'db_connection'):
            self.db_connection.close()

    def __compress_knp_result(self, knp_parsed_result):
        # type: (Optional[text_type])->Union[text_type, Optional[bytes]]
        if knp_parsed_result is None:
            return None
        else:
            if self.is_compress:
                if PY2:
                    return zlib.compress(knp_parsed_result)
                elif PY3:
                    return zlib.compress(knp_parsed_result.encode('utf-8'))
            else:
                return knp_parsed_result

    def __decompress_knp_result(self, knp_parsed_result):
        # type: (Optional[bytes])->Union[bytes, Optional[bytes]]
        if knp_parsed_result is None:
            return None
        else:
            if self.is_compress:
                if PY2:
                    return zlib.decompress(knp_parsed_result)
                elif PY3:
                    return zlib.decompress(knp_parsed_result).decode('utf-8')
            else:
                return knp_parsed_result

    def create_db(self):
        # type: () -> None
        """"""
        cur = self.db_connection.cursor()
        sql = """create table if not exists {table_name} (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        parsed_result TEXT,
        status BOOLEAN,
        is_success BOOLEAN,
        sub_id TEXT,
        sentence_index  INTEGER,
        created_at DATETIME,
        updated_at DATETIME,
        document_args TEXT)"""
        cur.execute(sql.format(table_name=self.table_name_text))
        self.db_connection.commit()
        cur.close()

    def insert_record(self, document_obj):
        # type: (DocumentObject) -> bool
        """You initialize record for input
        """
        sql_check = "SELECT count(record_id) FROM {} WHERE record_id = ?".format(self.table_name_text)
        cur = self.db_connection.cursor()
        cur.execute(sql_check, (document_obj.record_id,))
        if cur.fetchone()[0] >= 1:
            cur.close()
            return False
        else:
            sql_insert = """INSERT INTO {}(record_id, text, parsed_result, status, is_success, sub_id, sentence_index, created_at, updated_at, document_args)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(self.table_name_text)
            cur = self.db_connection.cursor()
            try:
                doc_args = None if document_obj.document_args is None else json.dumps(document_obj.document_args, ensure_ascii=False)
                __parsed_result = self.__compress_knp_result(document_obj.parsed_result)
                cur.execute(sql_insert, (document_obj.record_id,
                                         document_obj.text,
                                         __parsed_result,
                                         document_obj.status,
                                         document_obj.is_success,
                                         document_obj.sub_id,
                                         document_obj.sentence_index,
                                         document_obj.timestamp,
                                         document_obj.updated_at,
                                         doc_args))
                self.db_connection.commit()
                cur.close()
            except Exception as e:
                self.db_connection.rollback()
                logger.error(traceback.format_exc())
                raise Exception(e)

    def insert_multiple(self, seq_document_obj):
        # type: (List[DocumentObject])->bool
        sql_insert = """INSERT INTO {}(
        record_id, 
        text, 
        parsed_result, 
        status, 
        is_success, 
        sub_id, 
        sentence_index, 
        created_at, 
        updated_at, 
        document_args)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(self.table_name_text)
        cur = self.db_connection.cursor()
        cur.execute("PRAGMA synchronous = OFF")
        cur.execute("BEGIN TRANSACTION")
        __records = [(
            d.record_id,
            d.text,
            self.__compress_knp_result(d.parsed_result),
            d.status,
            d.is_success,
            d.sub_id,
            d.sentence_index,
            d.timestamp,
            d.updated_at,
            None if d.document_args is None else json.dumps(d.document_args, ensure_ascii=False)
        ) for d in seq_document_obj]
        set_record_ids = set(self.get_record_ids())
        records = [t for t in __records if t[0] not in set_record_ids]
        assert len(records) > 0
        try:
            cur.executemany(sql_insert, records)
            self.db_connection.commit()
        except Exception as e:
            self.db_connection.rollback()
            logger.error(traceback.format_exc())
            raise Exception(e)

        return True

    def update_record(self, document_obj):
        # type: (DocumentObject)->bool
        """Updates some columns after KNP parsing process. It tries to update operation many times.
        """

        sql_update = "UPDATE {} SET status=?, is_success=?, parsed_result=? WHERE record_id = ?".format(self.table_name_text)
        is_success = False
        i = 0
        while is_success is False:
            try:
                if six.PY2 and isinstance(document_obj.parsed_result, six.text_type):
                    parsed_result = document_obj.parsed_result.encode('utf-8')
                else:
                    parsed_result = document_obj.parsed_result

                __parsed_result = self.__compress_knp_result(parsed_result)
                cur = self.db_connection.cursor()
                cur.execute(sql_update, (True, document_obj.is_success, __parsed_result, document_obj.record_id,))
                self.db_connection.commit()
                cur.close()
            except Exception as e:
                # wait until next try
                logger.error(traceback.format_exc())
                self.db_connection.rollback()
                logger.info(msg='It waits {} sec. to avoid a conflict.'.format(self.sleep_time))
                time.sleep(self.sleep_time)
                i += 1
            else:
                is_success = True
                break
            if i == self.n_retry:
                self.db_connection.rollback()
                logger.error(msg='We wait {} times to avoid conflict, however it does NOT resolve. We record it as error.'.format(self.n_retry))
                return False

        return True

    def get_one_record(self, record_id):
        # type: (int)->Union[bool,DocumentObject]
        """Get document object with record_id.

        :param record_id: unique and sequential id
        :return: document object
        """
        sql_ = "SELECT record_id, text, parsed_result, status, is_success, sub_id, sentence_index, created_at, updated_at FROM {} WHERE record_id = ?".format(self.table_name_text)

        is_success = False
        i = 0
        while is_success is False:
            try:
                cur = self.db_connection.cursor()
                cur.execute(sql_, (record_id, ))
                fetched_record = cur.fetchone()
            except:
                logger.error(traceback.format_exc())
                self.db_connection.rollback()
                logger.info(msg='It waits {} sec. to avoid a conflict.'.format(self.sleep_time))
                time.sleep(self.sleep_time)
                i += 1
            else:
                is_success = True
                cur.close()
                break
            if i == self.n_retry:
                self.db_connection.rollback()
                logger.error(msg='We wait {} times to avoid conflict, however it does NOT resolve. We record it as error.'.format(self.n_retry))
                return False

        __parsed_result = self.__decompress_knp_result(fetched_record[2])
        return DocumentObject(
            record_id=fetched_record[0],
            text=fetched_record[1],
            parsed_result=__parsed_result,
            status=fetched_record[3],
            is_success=fetched_record[4],
            sub_id=fetched_record[5],
            sentence_index=fetched_record[6],
            timestamp=fetched_record[7],
            updated_at=fetched_record[8])

    def get_one_record_sub_id(self, sub_id):
        # type: (int)->DocumentObject
        """Get document object with sub_id record.

        :param sub_id: normally text id of original text.
        :return: Document object with sub_id
        """
        sql_ = """SELECT 
        record_id, 
        text, 
        parsed_result, 
        status, 
        is_success, 
        sub_id, 
        sentence_index, 
        created_at, 
        updated_at
        FROM {} WHERE sub_id = ?""".format(self.table_name_text)

        is_success = False
        i = 0
        while is_success is False:
            try:
                cur = self.db_connection.cursor()
                cur.execute(sql_, (sub_id,))
                fetched_record = cur.fetchone()
            except:
                logger.error(traceback.format_exc())
                self.db_connection.rollback()
                logger.info(msg='It waits {} sec. to avoid a conflict.'.format(self.sleep_time))
                time.sleep(self.sleep_time)
                i += 1
            else:
                is_success = True
                cur.close()
                break
            if i == self.n_retry:
                self.db_connection.rollback()
                return False

        if fetched_record is None:
            return None
        else:
            __parsed_result = self.__decompress_knp_result(fetched_record[2])
            return DocumentObject(
                record_id=fetched_record[0],
                text=fetched_record[1],
                parsed_result=__parsed_result,
                status=fetched_record[3],
                is_success=fetched_record[4],
                sub_id=fetched_record[5],
                sentence_index=fetched_record[6],
                timestamp=fetched_record[7],
                updated_at=fetched_record[8])

    def get_record(self, is_use_generator=False):
        # type: (bool)->Union[Iterable[DocumentObject], List[DocumentObject]]
        """Get all records from db"""
        sql_ = """SELECT 
        record_id, 
        text, 
        parsed_result, 
        status, 
        is_success, 
        sub_id, 
        sentence_index, 
        created_at, 
        updated_at, 
        document_args
        FROM {}""".format(self.table_name_text)

        cur = self.db_connection.cursor()
        cur.execute(sql_)

        if six.PY3 and is_use_generator:
            seq_urls = (
                DocumentObject(
                    record_id=record_tuple[0],
                    text=record_tuple[1],
                    parsed_result=self.__decompress_knp_result(record_tuple[2]),
                    status=bool(record_tuple[3]),
                    is_success=bool(record_tuple[4]),
                    sub_id=record_tuple[5],
                    sentence_index=record_tuple[6],
                    timestamp=record_tuple[7],
                    updated_at=record_tuple[8],
                    document_args=None if record_tuple[9] is None else json.loads(record_tuple[9])
                ) for record_tuple in cur)
        else:
            if six.PY2:
                logger.warning('is_use_generator is invalid in Python2')

            seq_urls = [
                DocumentObject(
                    record_id=record_tuple[0],
                    text=record_tuple[1],
                    parsed_result=self.__decompress_knp_result(record_tuple[2]),
                    status=bool(record_tuple[3]),
                    is_success=bool(record_tuple[4]),
                    sub_id=record_tuple[5],
                    sentence_index=record_tuple[6],
                    timestamp=record_tuple[7],
                    updated_at=record_tuple[8],
                    document_args=None if record_tuple[9] is None else json.loads(record_tuple[9])
                ) for record_tuple in cur]

        return seq_urls

    def get_record_ids(self):
        # type: ()->List[int]
        """get all record ids from DB."""
        cur = self.db_connection.cursor()
        sql_fetch = "SELECT record_id FROM {}".format(self.table_name_text)
        cur.execute(sql_fetch)
        seq_ids = [record_tuple[0] for record_tuple in cur.fetchall()]

        return seq_ids

    def get_seq_ids_not_processed(self):
        """* What you can do
        - You get ids of document which are not processed yet
        """
        cur = self.db_connection.cursor()
        sql_fetch = "SELECT record_id FROM {} WHERE status = ?".format(self.table_name_text)
        cur.execute(sql_fetch, (False, ))
        seq_ids = [record_tuple[0] for record_tuple in cur.fetchall()]

        return seq_ids
