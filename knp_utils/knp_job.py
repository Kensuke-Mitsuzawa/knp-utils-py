#! -*- coding: utf-8 -*-
# package module
from knp_utils import models, db_handler
from knp_utils.db_handler import Sqlite3Handler
from knp_utils.models import KnpSubProcess, DocumentObject, ResultObject
# else
from typing import List, Tuple, Dict, Any, Callable
from more_itertools import chunked
from six import text_type
import joblib
import tempfile
import six
import uuid
import os
import re
import jaconv


def func_normalize_text(text):
    """* What you can do
    - It make normalize input text into text which is suitable to KNP analysis.
    """
    # type: (str)->str
    if six.PY2:
        if isinstance(text, str):
            text = text.decode('utf-8')
        return jaconv.h2z(text=re.sub(r'\s', '', string=text), kana=True, ascii=True, digit=True)
    else:
        return jaconv.h2z(text=re.sub(r'\s', '', string=text), kana=True, ascii=True, digit=True)


def parse_text_block(seq_record_id,
                     path_sqlite3_db_handler,
                     knp_command='/usr/local/bin/knp',
                     juman_command='/usr/local/bin/juman',
                     knp_options=None,
                     juman_options=None,
                     process_mode='everytime',
                     path_juman_rc=None,
                     is_normalize_text=False,
                     func_normalization=func_normalize_text):
    """* What you can do
    - It parses one input-document.
    """
    # type: (List[int],text_type,text_type,text_type,text_type,text_type,text_type,text_type,bool,Callable[[text_type],text_type])->bool

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
                                        is_use_jumanpp=is_use_jumanpp)

    process_db_handler = Sqlite3Handler(path_sqlite3_db_handler)
    for record_id in seq_record_id:
        document_obj = process_db_handler.get_one_record(record_id)
        if isinstance(document_obj, bool) and document_obj == False:
            return False
        if is_normalize_text:
            text = func_normalization(document_obj.text)
        else:
            text = document_obj.text

        parsed_result = knp_process_handler.run_command(text=text)  # type: Tuple[bool,six.text_type]
        document_obj.set_knp_parsed_result(t_parsed_result=parsed_result)
        process_db_handler.update_record(document_obj)

    return True


def parse_texts(path_sqlite3_db_handler,
                n_jobs,
                knp_command='/usr/local/bin/knp',
                juman_command='/usr/local/bin/juman',
                knp_options=None,
                juman_options=None,
                path_juman_rc=None,
                process_mode='pexpect',
                is_normalize_text=True,
                func_normalization=func_normalize_text):
    """* What you can do
    - It takes many documents and parse them
    """
    # type: (text_type,int,text_type,text_type,text_type,text_type,text_type,text_type,bool,Callable[[text_type],text_type])->bool
    seq_ids_to_process = Sqlite3Handler(path_sqlite3_db_handler).get_seq_ids_not_processed()
    # Run KNP process in parallel #
    if n_jobs==-1:
        seq_block_record_id = chunked(seq_ids_to_process, n=8)
    else:
        seq_block_record_id = chunked(seq_ids_to_process, n_jobs)

    joblib.Parallel(n_jobs=n_jobs, backend='threading')(joblib.delayed(parse_text_block)(
        seq_record_id=block_record_id,
        path_sqlite3_db_handler=path_sqlite3_db_handler,
        knp_command=knp_command,
        juman_command=juman_command,
        knp_options=knp_options,
        juman_options=juman_options,
        process_mode=process_mode,
        path_juman_rc=path_juman_rc,
        is_normalize_text=is_normalize_text,
        func_normalization=func_normalization
    ) for block_record_id in seq_block_record_id)

    return True


def initialize_text_db(seq_document_obj, work_dir=tempfile.mkdtemp(), file_name=str(uuid.uuid4())):
    """* What you can do
    """
    # type: (List[DocumentObject],str,str)->None
    sqlite3_db_handler = Sqlite3Handler(path_sqlite_file=os.path.join(work_dir, file_name))
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


def split_sentence(text):
    """* What you can do
    - 文分割を実施する
    * Output
    - (文番号,分割済みテキスト)のタプル
    """
    # type: (str)->List[Tuple[int,str]]
    eos_pattern = re.compile("(?P<mark>[。|！|？|\u2753|\u2757|\u2049|\n]+)")
    particle_pattern = re.compile("(?P<mark>[！|？|\u2753|\u2757|\u2049]+)[$$]+(?P<particle>[が|を|に|と|の|で|や|って])")
    bracket_pattern = re.compile("(?P<quote>「.*?」|『.*?』|（.*?）)")
    start_mark_pattern = re.compile("(?P<mark>[\u2010-\u266F])")
    break_pattern = re.compile("[$$]+")

    # 改行の削除
    # ただし、読点が投稿中に含まれない場合には、改行を文区切りとみなす
    if "。" not in text:
        pass
    else:
        text = text.replace("\n", "")

    # 文末と判断できる場合すべてに、区切り文字'$$'を挿入する
    # ただし、投稿の最後にもつけると空文ができるので、最後はrstripで落とす
    text = eos_pattern.sub("\g<mark>$$", text).rstrip("$")

    # 助詞（らしき文字列）が続く区切り文字を削除
    # 「じゃらんのアプリの勧誘？がウザい。」のような場合に区切らないため
    text = particle_pattern.sub("\g<mark>\g<particle>", text)

    # カッコ内に含まれる区切り文字を削除
    repl_func = lambda match_obj: match_obj.group("quote").replace("$$", "")
    text = bracket_pattern.sub(repl_func, text)

    # 記号ではじまる投稿は、箇条書き形式の場合であると仮定し、その記号の前にも区切り文字を挿入する
    if start_mark_pattern.match(text):
        text = start_mark_pattern.sub("$$\g<mark>", text).lstrip("$$")

    # 最終的に残った区切り文字で分割
    return [(sent_id, sentence.strip()) for sent_id, sentence in enumerate(break_pattern.split(text))]


def generate_record_data_model_obj(seq_input_obj,
                                   is_split_sentence):
    """* What you can do
    - 入力データをオブジェクト化してしまう。
    - 文単位管理の可能性があるので、不満用とオブジェクトと同じものを使う
    """
    # type: (List[Dict[str,Any]], bool)->List[DocumentObject]
    seq_record_data_model = []
    record_id = 0
    for dict_document in seq_input_obj:
        __check_dict_document(dict_document)
        # ===========================================================================================================
        if is_split_sentence:
            """文分割の実施"""
            for tuple_sentid_text in split_sentence(dict_document['text']):
                sentence, sentence_index = tuple_sentid_text[1], tuple_sentid_text[0]
                record_data_model = DocumentObject(
                    record_id=record_id,
                    text=sentence,
                    status=False,
                    parsed_result=None,
                    sub_id=dict_document['text-id'],
                    sentence_index=sentence_index)
                seq_record_data_model.append(record_data_model)
                record_id += 1
        else:
            """文分割は実施しない"""
            record_data_model = DocumentObject(
            record_id=record_id,
            text=dict_document['text'],
            status=False,
            parsed_result=None,
            sub_id=dict_document['text-id'])

            seq_record_data_model.append(record_data_model)
            record_id += 1
        # ===========================================================================================================
    return seq_record_data_model



def generate_document_objects(seq_input_dict_document):
    """* What you can do
    """
    # type: (List[Dict[str,Any]],) -> List[DocumentObject]
    seq_document_obj = []
    for index_id, dict_document in enumerate(seq_input_dict_document):
        __check_dict_document(dict_document)

        seq_document_obj.append(DocumentObject(
            record_id=index_id,
            sentence_index=0,
            text=dict_document['text'],
            status=False,
            parsed_result=None,
            sub_id=dict_document['text-id']
        ))
    return seq_document_obj


def main(seq_input_dict_document,
         n_jobs=-1,
         work_dir=tempfile.mkdtemp(),
         file_name=str(uuid.uuid4()),
         knp_command='/usr/local/bin/knp',
         juman_command='/usr/local/bin/juman',
         knp_options=None,
         juman_options=None,
         path_juman_rc=None,
         process_mode='everytime',
         is_get_processed_doc=True,
         is_delete_working_db=True,
         is_normalize_text=False,
         is_split_text=False,
         func_normalization=func_normalize_text):
    """*What you can do
    -
    * Args
    - seq_input_dict_document
        - List of input document
        >>> [{"input-id": "input-1", "text": "これは入力テキストです。"}]
    - work_dir
        - path into directory where working-db is saved
    - file_name
        - file name of working sqlite3-db file
    - knp_command
        - Path to KNP
    - juman_command
        - Path to Juman. You can set path to Juman++ also
    - path_juman_rc
        - Path to Jumanrc(config file) if you have
    - process_mode
        - A way to manage processes in multi-thread.
            - "pexpect": Faster. It keep processes running in each thread.
            - "everytime": Slower. It launches a process when one data comes. 
    - is_delete_working_db
        - Boolean flag if you save working sqlite3 db file or Not
    - is_get_processed_doc
        - Boolean flag if you get processed document or Not. KNP result string tends to be super big. So, if you put a lot of document, I strongly recomment to put is_get_processed_doc == False.
         And use Sqlite3Handler(path_sqlite_file=path_working_db).get_record(is_use_generator=True).
    """
    # type: (List[Dict[str,Any]],int,text_type,text_type,text_type,text_type,text_type,text_type,text_type,text_type,bool,bool,bool,bool,Callable[[text_type],text_type])->ResultObject
    if is_delete_working_db and is_get_processed_doc == False:
        raise Exception('Nothing is return object when is_delete_working_db = True and is_get_processed_doc = False')

    path_working_db = os.path.join(work_dir, file_name)
    if is_split_text:
        seq_doc_obj = generate_record_data_model_obj(seq_input_dict_document, is_split_sentence=True)
    else:
        seq_doc_obj = generate_document_objects(seq_input_dict_document)
    # insert object into backendDB #
    initialize_text_db(seq_document_obj=seq_doc_obj, work_dir=work_dir, file_name=file_name)
    # Run KNP analysis in parallel #
    parse_texts(path_sqlite3_db_handler=path_working_db,
                n_jobs=n_jobs,
                knp_command=knp_command,
                juman_command=juman_command,
                juman_options=juman_options,
                knp_options=knp_options,
                process_mode=process_mode,
                path_juman_rc=path_juman_rc,
                is_normalize_text=is_normalize_text,
                func_normalization=func_normalization)

    if is_get_processed_doc:
        seq_processed_doc_obj = Sqlite3Handler(path_sqlite_file=path_working_db).get_record()
    else:
        seq_processed_doc_obj = []

    if is_delete_working_db:
        if os.path.exists(path_working_db): os.remove(path_working_db)
        return models.ResultObject(seq_processed_doc_obj, path_working_db=None, db_handler=None)
    else:
        return models.ResultObject(seq_processed_doc_obj,
                                   path_working_db=path_working_db,
                                   db_handler=Sqlite3Handler(path_sqlite_file=path_working_db))