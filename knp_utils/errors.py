#! -*- coding: utf-8 -*-
from six import text_type
from typing import Dict, Any


class ParserIntializeError(Exception):
    def __init__(self, message, path_to_parser=None, error_line=None, status='error'):
        """"""
        # type: (text_type,text_type,text_type,text_type)->None
        self.message=message
        self.error_line = error_line
        self.status = status
        self.path_to_parser = path_to_parser

    def to_dict(self):
        """"""
        # type: ()->Dict[text_type,Any]
        rv = {'message': self.message, 'error_line': self.error_line, 'status_code':self.status}

        return rv