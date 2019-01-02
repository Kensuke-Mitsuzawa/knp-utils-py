#! -*- coding: utf-8 -*-
from typing import List, Union
from knp_utils.models import DocumentObject

class DbHandler(object):
    def insert_record(self, document_obj):
        # type: (DocumentObject)->bool
        raise NotImplementedError()

    def get_record(self, is_use_generator):
        # type: (bool)->List[DocumentObject]
        raise NotImplementedError()

    def get_one_record(self, record_id):
        # type: (int)->Union[bool,DocumentObject]
        raise NotImplementedError()

    def get_seq_ids_not_processed(self):
        # type: ()->List[str]
        raise NotImplementedError()

    def update_record(self, document_obj):
        # type: (DocumentObject)->bool
        raise NotImplementedError()
