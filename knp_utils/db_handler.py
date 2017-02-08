#! -*- coding: utf-8 -*-
from typing import List, Tuple, Dict, Union, Iterable
from knp_utils import logger_unit
import os
import traceback
from datetime import datetime
import sqlite3
import six
logger = logger_unit.logger


class DocumentObject(object):
    __slots__ = ('record_id', 'status', 'text',
                 'is_success', 'timestamp', 'updated_at', 'sub_id', 'parsed_result')

    def __init__(self,
                 record_id,
                 text,
                 status,
                 parsed_result=None,
                 is_success=None,
                 sub_id=None,
                 timestamp = datetime.now(),
                 updated_at = datetime.now()):
        # type: (int,str,bool,Union[None,str],bool,str,datetime,datetime) -> None

        if six.PY2:
            if isinstance(text, str):
                self.text = text.decode('utf-8')
            else:
                self.text = text

            if isinstance(sub_id, str):
                self.sub_id = sub_id.decode('utf-8')
            else:
                self.sub_id = sub_id

            if isinstance(parsed_result, str):
                self.parsed_result = parsed_result.decode('utf-8')
            else:
                self.parsed_result = parsed_result
        else:
            self.text = text
            self.sub_id = sub_id
            self.parsed_result = parsed_result

        self.record_id = record_id
        self.status = status
        self.timestamp = timestamp
        self.updated_at = updated_at
        self.is_success = is_success

    def set_knp_parsed_result(self, parsed_result):
        """* What you can do
        - It sets KNP parsed result
        """
        # type: (str)->None
        is_success_flag = self.__check_knp_result(parsed_result=parsed_result)
        self.is_success = is_success_flag
        self.parsed_result = parsed_result

    def __check_knp_result(self, parsed_result):
        """* What you can do
        - It checks if knp result is error or not
        """
        # type: (str)->bool
        if 'error' in parsed_result.lower():
            return False
        else:
            return True

    def to_dict(self):
        """* What you can do
        - You see parsed result with dict format
        """
        # type: ()->Dict[str,Any]
        return {
            "record_id": self.record_id,
            "sub_id": self.sub_id,
            "status": self.status,
            "text": self.text,
            "is_success": self.is_success,
            "parsed_result": self.parsed_result,
            "timestamp": self.timestamp,
            "update_at": self.updated_at
        }


class DbHandler(object):
    def insert_record(self, document_obj):
        """"""
        # type: (DocumentObject)->bool
        raise NotImplementedError()

    def get_record(self, is_use_generator):
        """"""
        # type: (bool)->List[DocumentObject]
        raise NotImplementedError()

    def get_seq_ids_not_processed(self):
        """"""
        # type: ()->List[str]
        raise NotImplementedError()

    def update_record(self, document_obj):
        """"""
        # type: (DocumentObject)->bool
        raise NotImplementedError()


class Sqlite3Handler(DbHandler):
    def __init__(self,
                 path_sqlite_file,
                 table_name_text="text",
                 is_close_connection_end=True):
        """* Args
        - is_close_connection_end
            - If True, it deleted DB when a process is done. False; don't.
        """
        # type: (str,str,bool)->None
        self.table_name_text = table_name_text
        self.is_close_connection_end = is_close_connection_end
        self.path_sqlite_file = path_sqlite_file
        if not os.path.exists(self.path_sqlite_file):
            self.db_connection = sqlite3.connect(database=self.path_sqlite_file)
            self.db_connection.text_factory = str
            self.create_db()
        else:
            self.db_connection = sqlite3.connect(database=self.path_sqlite_file)
            self.db_connection.text_factory = str

    def __del__(self):
        if self.is_close_connection_end and hasattr(self, 'db_connection'):
            self.db_connection.close()

    def create_db(self):
        # type: () -> None
        cur = self.db_connection.cursor()
        sql = """create table if not exists {table_name} (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        parsed_result TEXT,
        status BOOLEAN,
        is_success BOOLEAN,
        sub_id TEXT,
        created_at DATETIME,
        updated_at DATETIME)"""
        cur.execute(sql.format(table_name=self.table_name_text))
        self.db_connection.commit()
        cur.close()

    def insert_record(self, document_obj):
        # type: (DocumentObject) -> bool
        """* What you can do
        - You initialize record for input
        """
        sql_check = "SELECT count(record_id) FROM {} WHERE record_id = ?".format(self.table_name_text)
        cur = self.db_connection.cursor()
        cur.execute(sql_check, (document_obj.record_id,))
        if cur.fetchone()[0] >= 1:
            cur.close()
            return False
        else:
            sql_insert = """INSERT INTO {}(record_id, text, parsed_result, status, is_success, sub_id, created_at, updated_at)
            values (?, ?, ?, ?, ?, ?, ?, ?)""".format(self.table_name_text)
            cur = self.db_connection.cursor()
            try:
                cur.execute(sql_insert, (document_obj.record_id,
                                         document_obj.text,
                                         document_obj.parsed_result,
                                         document_obj.status,
                                         document_obj.is_success,
                                         document_obj.sub_id,
                                         document_obj.timestamp,
                                         document_obj.updated_at))
                self.db_connection.commit()
                cur.close()
            except:
                logger.error(traceback.format_exc())
                self.db_connection.rollback()
                return False

    def update_record(self, document_obj):
        """* What you can do
        - It updates some columns after KNP parsing process.
        """
        # type: (DocumentObject)->bool
        sql_update = u"UPDATE {} SET status=?, parsed_result= ?, is_success = ? WHERE record_id = ?".format(self.table_name_text)
        cur = self.db_connection.cursor()
        try:
            cur.execute(sql_update, (True, document_obj.parsed_result, document_obj.is_success, document_obj.record_id,))
            self.db_connection.commit()
            cur.close()
        except:
            logger.error(traceback.format_exc())
            self.db_connection.rollback()
            return False

        return True

    def get_one_record(self, record_id):
        # type: (int)->DocumentObject
        sql_ = """SELECT record_id, text, parsed_result, status, is_success, sub_id, created_at, updated_at
        FROM {} WHERE record_id = ?""".format(self.table_name_text)

        cur = self.db_connection.cursor()
        cur.execute(sql_, (record_id, ))
        fetched_record = cur.fetchone()

        return DocumentObject(
            record_id=fetched_record[0],
            text=fetched_record[1],
            parsed_result=fetched_record[2],
            status=fetched_record[3],
            is_success=fetched_record[4],
            sub_id=fetched_record[5],
            timestamp=fetched_record[6],
            updated_at=fetched_record[7])

    def get_one_record_sub_id(self, sub_id):
        """"""
        # type: (int)->DocumentObject
        sql_ = """SELECT record_id, text, parsed_result, status, is_success, sub_id, created_at, updated_at
        FROM {} WHERE sub_id = ?""".format(self.table_name_text)

        cur = self.db_connection.cursor()
        cur.execute(sql_, (sub_id,))
        fetched_record = cur.fetchone()
        if fetched_record is None:
            return None
        else:
            return DocumentObject(
                record_id=fetched_record[0],
                text=fetched_record[1],
                parsed_result=fetched_record[2],
                status=fetched_record[3],
                is_success=fetched_record[4],
                sub_id=fetched_record[5],
                timestamp=fetched_record[6],
                updated_at=fetched_record[7])

    def get_record(self, is_use_generator=False):
        """"""
        # type: (bool)->Union[Iterable[DocumentObject]], List[DocumentObject]
        sql_ = """SELECT record_id, text, parsed_result, status, is_success, sub_id, created_at, updated_at
        FROM {}""".format(self.table_name_text)

        cur = self.db_connection.cursor()
        cur.execute(sql_)

        if six.PY3 and is_use_generator:
            seq_urls = (
                DocumentObject(
                    record_id=record_tuple[0],
                    text=record_tuple[1],
                    parsed_result=record_tuple[2],
                    status=record_tuple[3],
                    is_success=record_tuple[4],
                    sub_id=record_tuple[5],
                    timestamp=record_tuple[6],
                    updated_at=record_tuple[7]
                ) for record_tuple in cur)
        else:
            if six.PY2:
                logger.warning('is_use_generator is invalid in Python2')

            seq_urls = [
                DocumentObject(
                    record_id=record_tuple[0],
                    text=record_tuple[1],
                    parsed_result=record_tuple[2],
                    status=record_tuple[3],
                    is_success=record_tuple[4],
                    sub_id=record_tuple[5],
                    timestamp=record_tuple[6],
                    updated_at=record_tuple[7]
                ) for record_tuple in cur]

        return seq_urls

    def get_seq_ids_not_processed(self):
        """* What you can do
        - You get ids of document which are not processed yet
        """
        cur = self.db_connection.cursor()
        sql_fetch = "SELECT record_id FROM {} WHERE status = ?".format(self.table_name_text)
        cur.execute(sql_fetch, (False, ))
        seq_ids = [record_tuple[0] for record_tuple in cur.fetchall()]

        return seq_ids
