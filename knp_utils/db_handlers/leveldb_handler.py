#! -*- coding: utf-8 -*-
from typing import Iterator, Tuple, Any, Union
from knp_utils.logger_unit import logger
from knp_utils.models import DocumentObject
from knp_utils.db_handlers.base import DbHandler
from leveldb import LevelDB
from six import PY2, PY3
import cloudpickle
import leveldb
import zlib

KeyType = Union[str, int]


class LevelDbHandler(DbHandler):
    def __init__(self, db_obj, is_compress=True):
        # type: (LevelDB, bool)->None
        self.is_compress = is_compress
        self.db_obj = db_obj
        self.__n_record = 0
        self.__keys = []
        for t in self.iter_items():
            self.__n_record += 1
            self.__keys.append(t[0])

    def __del__(self):
        del self.db_obj

    def write(self, key, value_obj):
        # type: (KeyType, Any)->None
        assert isinstance(key, (str, int))
        a = cloudpickle.dumps(value_obj)
        b = zlib.compress(a)
        __key = str(key).encode()
        self.__n_record += 1
        self.__keys.append(key)
        self.db_obj.Put(__key, b)

    def load(self, key):
        # type: (KeyType)->Any
        assert isinstance(key, (int, str))
        __key = key.encode()
        __obj_compress = self.db_obj.Get(__key)
        return cloudpickle.loads(zlib.decompress(__obj_compress))

    def iter_items(self):
        # type: ()->Iterator[Tuple[KeyType, Any]]
        for t_record in self.db_obj.RangeIter():
            k = t_record[0].decode()
            v = cloudpickle.loads(zlib.decompress(t_record[1]))
            yield k, v

    def insert_record(self, document_obj):
        # type: (DocumentObject)->None
        key = document_obj.record_id
        self.write(key=key, value_obj=document_obj)

    def get_record(self, is_use_generator):
        # type: (bool)->Iterator[DocumentObject]
        if is_use_generator:
            return self.values()
        else:
            return list(self.values())

    def get_seq_ids_not_processed(self):
        # type: ()->Iterator[Tuple[KeyType, Any]]
        """Get record-id which is not processed yet."""
        for key, value in self.iter_items():
            assert isinstance(value, DocumentObject)
            if value.status is True:
                continue
            else:
                yield key

    def get_one_record(self, record_id):
        # type: (KeyType)->Union[bool,DocumentObject]
        return self.load(record_id)

    def update_record(self, document_obj):
        # type: (DocumentObject)->None
        """delete object with given key first and put new document_obj.
        This is because leveldb does not have update operation."""
        key = document_obj.record_id
        assert self.__contains__(key)
        __key = key.encode()
        # delete old key
        self.db_obj.Delete(__key)
        # put new document
        self.write(key, document_obj)

    def keys(self):
        return self.__keys

    def values(self):
        for t_record in self.db_obj.RangeIter():
            v = cloudpickle.loads(zlib.decompress(t_record[1]))
            yield v

    def items(self):
        return self.iter_items()

    def __iter__(self):
        for t_record in self.db_obj.RangeIter():
            k = t_record[0].decode()
            yield k

    def __contains__(self, item):
        try:
            value = self.load(item)
            return True
        except KeyError:
            return False

    def __setitem__(self, key, value):
        self.write(key, value)

    def __getitem__(self, item):
        return self.load(item)

    def __len__(self):
        return self.__n_record

