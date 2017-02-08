#! -*- coding: utf-8 -*-
from typing import List, Tuple, Dict, Any, Callable
from knp_utils import models, db_handler
import joblib
import tempfile
import six
import uuid
import os
import re
import jaconv


def func_normalize_text(text):
    """"""
    # type: (str)->str
    if six.PY2:
        if isinstance(text, str):
            text = text.decode('utf-8')
        return jaconv.h2z(text=re.sub(r'\s', '', string=text), kana=True, ascii=True, digit=True)
    else:
        return jaconv.h2z(text=re.sub(r'\s', '', string=text), kana=True, ascii=True, digit=True)


def parse_one_text(record_id,
                   path_sqlite3_db_handler,
                   argument_params,
                   is_normalize_text=False,
                   func_normalization=func_normalize_text):
    """* What you can do
    - It parses one input-document.
    """
    # type: (int,db_handler.Sqlite3Handler,models.Params,bool,Callable[[str],str])->bool

    process_db_handler = db_handler.Sqlite3Handler(path_sqlite3_db_handler)
    document_obj = process_db_handler.get_one_record(record_id)
    if is_normalize_text:
        text = func_normalization(document_obj.text)
    else:
        text = document_obj.text

    parsed_result = argument_params.run_command(text=text)
    document_obj.set_knp_parsed_result(parsed_result=parsed_result)
    process_db_handler.update_record(document_obj)
    del process_db_handler

    return True


def parse_texts(argument_params,
                path_sqlite3_db_handler,
                is_normalize_text=False,
                func_normalization=func_normalize_text):
    """* What you can do
    - It takes many documents and parse them
    """
    # type: (models.Params,str,bool,Callable[[str],str])->bool
    seq_ids_to_process = db_handler.Sqlite3Handler(path_sqlite3_db_handler).get_seq_ids_not_processed()
    joblib.Parallel(n_jobs=argument_params.n_jobs, backend='threading')(joblib.delayed(parse_one_text)(
        record_id=record_id,
        path_sqlite3_db_handler=path_sqlite3_db_handler,
        argument_params=argument_params,
        is_normalize_text=is_normalize_text,
        func_normalization=func_normalization
    ) for record_id in seq_ids_to_process)

    return True


def initialize_text_db(seq_document_obj, work_dir=tempfile.mkdtemp(), file_name=str(uuid.uuid4())):
    """* What you can do
    """
    # type: (List[db_handler.DocumentObject],str,str)->None
    sqlite3_db_handler = db_handler.Sqlite3Handler(path_sqlite_file=os.path.join(work_dir, file_name))
    [
        sqlite3_db_handler.insert_record(document_obj)
        for document_obj in seq_document_obj
    ]

    return True


def __check_dict_document(dict_object):
    """* What you can do
    - It checks if document is correct or Not
    """
    # type: (Dict[str,List[str]])->bool
    if not "text" in dict_object:
        raise Exception("Your input does not have key = 'text'")
    if not "text-id" in dict_object:
        raise Exception("Your input does not have key = 'text-id'")

    return True


def generate_document_objects(seq_input_dict_document):
    """* What you can do
    """
    # type: (List[Dict[str,Any]],) -> List[db_handler.DocumentObject]
    seq_document_obj = []
    for index_id, dict_document in enumerate(seq_input_dict_document):
        __check_dict_document(dict_document)

        seq_document_obj.append(db_handler.DocumentObject(
            record_id=index_id,
            text=dict_document['text'],
            status=False,
            parsed_result=None,
            sub_id=dict_document['text-id']
        ))
    return seq_document_obj


def main(seq_input_dict_document,
         argument_params,
         work_dir=tempfile.mkdtemp(),
         file_name=str(uuid.uuid4()),
         is_get_processed_doc=True,
         is_delete_working_db=True,
         is_normalize_text=False,
         func_normalization=func_normalize_text,):
    """*What you can do
    -
    * Args
    - seq_input_dict_document
        - List of input document
        >>> [{"input-id": "input-1", "text": "これは入力テキストです。"}]
    - argument_params
        - Argument parameter object
    - work_dir
        - path into directory where working-db is saved
    - file_name
        - file name of working sqlite3-db file
    - is_delete_working_db
        - Boolean flag if you save working sqlite3 db file or Not
    - is_get_processed_doc
        - Boolean flag if you get processed document or Not. KNP result string tends to be super big. So, if you put a lot of document, I strongly recomment to put is_get_processed_doc == False.
         And use db_handler.Sqlite3Handler(path_sqlite_file=path_working_db).get_record(is_use_generator=True).
    """
    # type: (List[Dict[str,Any]],models.Params,str,str,bool,bool,bool,Callable[[str],str])->models.ResultObject
    if is_delete_working_db and is_get_processed_doc == False:
        raise Exception('Nothing is return object when is_delete_working_db = True and is_get_processed_doc = False')


    path_working_db = os.path.join(work_dir, file_name)
    seq_doc_obj = generate_document_objects(seq_input_dict_document)
    initialize_text_db(seq_document_obj=seq_doc_obj, work_dir=work_dir, file_name=file_name)
    parse_texts(argument_params, path_working_db, is_normalize_text=is_normalize_text, func_normalization=func_normalization)

    if is_get_processed_doc:
        seq_processed_doc_obj = db_handler.Sqlite3Handler(path_sqlite_file=path_working_db).get_record()
    else:
        seq_processed_doc_obj = []

    if is_delete_working_db:
        if os.path.exists(path_working_db): os.remove(path_working_db)
        return models.ResultObject(seq_processed_doc_obj, path_working_db=None, db_handler=None)
    else:
        return models.ResultObject(seq_processed_doc_obj,
                                   path_working_db=path_working_db,
                                   db_handler=db_handler.Sqlite3Handler(path_sqlite_file=path_working_db))