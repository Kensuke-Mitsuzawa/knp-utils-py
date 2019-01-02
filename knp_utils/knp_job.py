#! -*- coding: utf-8 -*-
# package module
from knp_utils import models
from knp_utils.db_handlers import Sqlite3Handler
from knp_utils.models import KnpSubProcess, DocumentObject, ResultObject
from knp_utils.utils import func_normalize_text, generate_record_data_model_obj, generate_document_objects
from knp_utils.logger_unit import logger
# else
from typing import List, Tuple, Dict, Any, Callable, Iterator
from more_itertools import chunked
from six import text_type
import joblib
import tempfile
import six
import uuid
import os


def parse_text_block(seq_record_id,
                     path_db_handler,
                     knp_command='/usr/local/bin/knp',
                     juman_command='/usr/local/bin/juman',
                     knp_options=None,
                     juman_options=None,
                     process_mode='subprocess',
                     path_juman_rc=None,
                     is_normalize_text=False,
                     timeout_seconds=60,
                     func_normalization=func_normalize_text,
                     backend='sqlite3'):
    # type: (List[int],text_type,text_type,text_type,text_type,text_type,text_type,text_type,bool,int,Callable[[text_type],text_type],str)->bool
    """It parses one input-document.
    """

    if os.path.basename(juman_command)=='jumanpp':
        is_use_jumanpp = True
    else:
        is_use_jumanpp = False
    knp_process_handler = KnpSubProcess(knp_command=knp_command,
                                        juman_command=juman_command,
                                        juman_options=juman_options,
                                        knp_options=knp_options,
                                        process_mode=process_mode,
                                        path_juman_rc=path_juman_rc,
                                        eos_pattern="EOS",
                                        is_use_jumanpp=is_use_jumanpp,
                                        timeout_second=timeout_seconds)

    assert os.path.exists(path_db_handler)
    if backend == 'sqlite3':
        process_db_handler = Sqlite3Handler(path_db_handler)
    else:
        raise Exception()

    for record_id in seq_record_id:
        document_obj = process_db_handler.get_one_record(record_id)
        if isinstance(document_obj, bool) and document_obj is False:
            return False
        if is_normalize_text:
            text = func_normalization(document_obj.text)
        else:
            text = document_obj.text

        parsed_result = knp_process_handler.run_command(text=text)  # type: Tuple[bool,six.text_type]
        document_obj.set_knp_parsed_result(t_parsed_result=parsed_result)
        process_db_handler.update_record(document_obj)

    return True


def parse_texts(path_db_handler,
                n_jobs,
                knp_command='/usr/local/bin/knp',
                juman_command='/usr/local/bin/juman',
                knp_options=None,
                juman_options=None,
                path_juman_rc=None,
                process_mode='subprocess',
                is_normalize_text=True,
                timeout_seconds=60,
                func_normalization=func_normalize_text,
                backend='sqlite3'):
    # type: (text_type,int,text_type,text_type,text_type,text_type,text_type,text_type,bool,int,Callable[[text_type],text_type],str)->bool
    """It takes many documents and parse them
    """
    assert os.path.exists(path_db_handler)
    if backend == 'sqlite3':
        seq_ids_to_process = Sqlite3Handler(path_db_handler).get_seq_ids_not_processed()
    else:
        raise Exception()

    # Run KNP process in parallel #
    if n_jobs == -1:
        seq_block_record_id = chunked(seq_ids_to_process, n=8)
    else:
        seq_block_record_id = chunked(seq_ids_to_process, n_jobs)

    joblib.Parallel(n_jobs=n_jobs, backend='threading')(joblib.delayed(parse_text_block)(
        seq_record_id=block_record_id,
        path_db_handler=path_db_handler,
        knp_command=knp_command,
        juman_command=juman_command,
        knp_options=knp_options,
        juman_options=juman_options,
        process_mode=process_mode,
        path_juman_rc=path_juman_rc,
        is_normalize_text=is_normalize_text,
        timeout_seconds=timeout_seconds,
        func_normalization=func_normalization,
        backend=backend
    ) for block_record_id in seq_block_record_id)

    return True


def initialize_text_db(seq_document_obj,
                       work_dir=tempfile.mkdtemp(),
                       file_name=str(uuid.uuid4()),
                       backend='sqlite3',
                       batch_size=5000):
    # type: (Iterator[DocumentObject], str, str, str, int)->bool
    logger.info('Inserting records into backend db...')
    if backend == 'sqlite3':
        sqlite3_db_handler = Sqlite3Handler(path_sqlite_file=os.path.join(work_dir, file_name))
        __batch_stack = []
        for document_obj in seq_document_obj:
            __batch_stack.append(document_obj)
            if len(__batch_stack) % batch_size == 0:
                sqlite3_db_handler.insert_multiple(__batch_stack)
                __batch_stack = []
        else:
            sqlite3_db_handler.insert_multiple(__batch_stack)
    else:
        raise Exception('No backend named {}'.format(backend))
    logger.info('Put all records into backend db!')
    return True


def main(seq_input_dict_document,
         n_jobs=-1,
         work_dir=tempfile.mkdtemp(),
         file_name=str(uuid.uuid4()),
         knp_command='/usr/local/bin/knp',
         juman_command='/usr/local/bin/juman',
         knp_options=None,
         juman_options=None,
         path_juman_rc=None,
         process_mode='subprocess',
         is_get_processed_doc=True,
         is_delete_working_db=True,
         is_normalize_text=False,
         is_split_text=False,
         timeout_seconds=60,
         func_normalization=func_normalize_text):
    # type: (List[Dict[str,Any]],int,text_type,text_type,text_type,text_type,text_type,text_type,text_type,text_type,bool,bool,bool,bool,int,Callable[[text_type],text_type])->ResultObject
    """
    :param seq_input_dict_document: (List, Iterator) of input document. "text-id" and "text" is mandatory field.
    You cloud put any information in "args" field. The dict object in "args" field must be possible to jsonize.
    >>> [{"text-id": "input-1", "text": "これは入力テキストです。", "args": {"date": "2018/12/12"}}]
    :param n_jobs: #thread to process.
    :param work_dir: path into directory where working-db is saved
    :param file_name: file name of working sqlite3-db file
    :param knp_command: Path to KNP
    :param juman_command: Path to Juman. You can set path to Juman++ also
    :param path_juman_rc: Path to Jumanrc(config file) if you have
    :param knp_options:
    :param juman_options:
    :param process_mode: A way to manage processes in multi-thread.
    "pexpect": Faster. It keep processes running in each thread.
    "everytime": Slower. It launches a process when one data comes.
    :param is_delete_working_db: Boolean flag if you save working sqlite3 db file or Not
    :param is_get_processed_doc: Boolean flag if you extract processed document after all parsing process is done.
    KNP result string tends to be super big.
    To avoid memory overflow, I strongly recommend to put is_get_processed_doc = False if you put a lot of document.
    If you put is_get_processed_doc == False, you could extract parsed document following method.
    >>> result_obj.db_handler.get_record()
    :param is_normalize_text:
    :param is_split_text:
    :param timeout_seconds:
    :param func_normalization:
    """
    if is_delete_working_db and is_get_processed_doc is False:
        raise Exception('Nothing is return object when is_delete_working_db = True and is_get_processed_doc = False')

    path_working_db = os.path.join(work_dir, file_name)
    if is_split_text:
        iter_doc_obj = generate_record_data_model_obj(seq_input_dict_document, is_split_sentence=True)
    else:
        iter_doc_obj = generate_document_objects(seq_input_dict_document)

    initialize_text_db(seq_document_obj=iter_doc_obj, work_dir=work_dir, file_name=file_name)

    # Run KNP analysis in parallel #
    parse_texts(path_db_handler=path_working_db,
                n_jobs=n_jobs,
                knp_command=knp_command,
                juman_command=juman_command,
                juman_options=juman_options,
                knp_options=knp_options,
                process_mode=process_mode,
                path_juman_rc=path_juman_rc,
                is_normalize_text=is_normalize_text,
                timeout_seconds=timeout_seconds,
                func_normalization=func_normalization)

    if is_get_processed_doc:
        logger.info('Loading processed documents from backend DB...')
        seq_processed_doc_obj = Sqlite3Handler(path_sqlite_file=path_working_db).get_record()
        logger.info('Loading end!')
    else:
        seq_processed_doc_obj = []

    if is_delete_working_db:
        if os.path.exists(path_working_db):
            os.remove(path_working_db)
        return models.ResultObject(seq_processed_doc_obj, path_working_db=None, db_handler=None)
    else:
        return models.ResultObject(seq_processed_doc_obj,
                                   path_working_db=path_working_db,
                                   db_handler=Sqlite3Handler(path_sqlite_file=path_working_db))
