#! -*- coding: utf-8 -*-
## flask package
from flask import Flask, render_template, request, redirect, url_for, jsonify
## typing
from typing import List, Dict, Any, Union, Tuple
## knp_utils
from knp_utils import knp_job, models, db_handler
from knp_utils.models import DocumentObject, KnpSubProcess
from knp_utils.utils import func_run_parsing, generate_record_data_model_obj, generate_document_objects
## to generate job-queue-id
import uuid
## postgresql
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
import psycopg2
# else
import pkg_resources
import os
import psutil
import traceback
from threading import Thread
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

flask_app = Flask(__name__)

############ You change following config depending on your app ############
flask_app.config.from_object('config.DevelopmentConfig')
# unix command path #
KNP_COMMAND = flask_app.config['KNP_COMMAND']
JUMAN_COMMAND = flask_app.config['JUMAN_COMMAND']
JUMANPP_COMMAND = flask_app.config['JUMANPP_COMMAND']
# psql connection #
PSQL_HOST = flask_app.config['PSQL_HOST']
PSQL_PORT = flask_app.config['PSQL_PORT']
PSQL_USER = flask_app.config['PSQL_USER']
PSQL_PASS = flask_app.config['PSQL_PASS']
PSQL_DB = flask_app.config['PSQL_DB']

TASK_STATUS = {
    "PENDING": 'PENDING',
    "FAILURE": 'FAILURE',
    "PROGRESS": 'PROGRESS',
    "DONE": 'DONE'
}


class PgBackendDbHandler(object):
    def __init__(self, db_connection, table_knp_result='knp_result', table_task_status='task_status'):
        # type: (connection, str, str)->None
        self.db_connection = db_connection
        self.table_knp_result = table_knp_result
        self.table_task_status = table_task_status

    def is_task_done(self,
                     task_id:str,
                     seq_document_sub_id:List[str])->Union[str,bool]:
        """* What u you can do
        - タスクが終わったことを確認する。
        - すべてのdocument sub-idがDBにinsertされたら、終了と判定する
        """
        sql_update = "SELECT text_id FROM {} WHERE task_id = %s".format(self.table_task_status)
        cur = self.db_connection.cursor()  # type: cursor
        try:
            cur.execute(sql_update, (task_id,))
            seq_text_id = [record[0] for record in cur.fetchall()]
        except:
            self.db_connection.rollback()
            return traceback.format_exc()
        else:
            if set(seq_document_sub_id) == set(seq_text_id):
                return True
            else:
                return False

    def insert_task_status_record(self,
                                  task_status=None,
                                  description=None,
                                  created_at=None,
                                  updated_at=None):
        """"""
        # type: (str,str,datetime,datetime)->Tuple[bool,str]
        sql_insert = "INSERT INTO {} (task_id, task_status, description, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)".format(self.table_task_status)

        task_id = str(uuid.uuid4())
        if task_status is None:
            task_status = TASK_STATUS['PENDING']
        if created_at is None:
            time_created_at = datetime.now()
        else:
            time_created_at = created_at

        if updated_at is None:
            time_updated_at = datetime.now()
        else:
            time_updated_at = updated_at

        cur = self.db_connection.cursor()  # type: cursor
        try:
            cur.execute(sql_insert, (task_id, task_status, description, time_created_at, time_updated_at))
            self.db_connection.commit()
        except:
            traceback_message = traceback.format_exc()
            return False, traceback_message
        else:
            cur.close()
            return True, task_id

    def update_task_status_record(self,
                                  task_id,
                                  task_status,
                                  description=None,
                                  time_at=None):
        """"""
        # type: (str,str,str,datetime)->Union[bool,str]

        sql_update = "UPDATE {} SET task_status=%s, description=%s, updated_at=%s WHERE task_id=%s".format(self.table_task_status)
        cur = self.db_connection.cursor()  # type: cursor
        if time_at is None:
            time_at = datetime.now()

        try:
            cur.execute(sql_update, (task_status, description, time_at, task_id))
            self.db_connection.commit()
        except:
            traceback_message = traceback.format_exc()
            return traceback_message
        else:
            cur.close()
            return True

    def insert_knp_result_record(self,
                                 task_id,
                                 text_id,
                                 sentence_index,
                                 knp_result,
                                 status,
                                 created_at):
        """"""
        # type: (str,str,int,str,bool,datetime)->Union[str,bool]
        sql_insert = "INSERT INTO {} (text_id,sentence_index,task_id,knp_result,status,created_at) VALUES (%s,%s,%s,%s,%s,%s)".format(self.table_knp_result)
        cur = self.db_connection.cursor()  # type: cursor
        boolen_status = bool(status)
        try:
            cur.execute(sql_insert, (text_id, sentence_index, task_id, knp_result, boolen_status, created_at))
            self.db_connection.commit()
        except:
            traceback_message = traceback.format_exc()
            self.db_connection.rollback()
            return traceback_message
        else:
            cur.close()
            return True

    def delete_knp_result_record(self, task_id):
        """"""
        # type: (str)->Union[str,bool]
        sql_delete = "DELETE FROM {} WHERE task_id = %s".format(self.table_knp_result)
        cur = self.db_connection.cursor()  # type: cursor
        try:
            cur.execute(sql_delete, (task_id,))
            self.db_connection.commit()
        except:
            traceback_message = traceback.format_exc()
            return traceback_message
        else:
            cur.close()
            return True

    def get_task_status(self, task_id):
        """"""
        # type: (str)->Union[str,Dict[str,Any]]

        sql_update = "SELECT task_status, description updated_at FROM {} WHERE task_id=%s".format(self.table_task_status)
        cur = self.db_connection.cursor(cursor_factory=RealDictCursor)  # type: cursor

        try:
            cur.execute(sql_update, (task_id, ))
            tasK_status_record = cur.fetchone()
        except:
            traceback_message = traceback.format_exc()
            return traceback_message
        else:
            cur.close()
            return tasK_status_record

    def get_processed_documents(self, task_id):
        """"""
        # type: (str)->Dict[str,Any]
        sql_update = "SELECT text_id,sentence_index,task_id,knp_result,status FROM {} WHERE task_id=%s".format(self.table_knp_result)
        cur = self.db_connection.cursor(cursor_factory=RealDictCursor)  # type: cursor

        try:
            cur.execute(sql_update, (task_id, ))
            task_status_record = cur.fetchall()
        except:
            traceback_message = traceback.format_exc()
            return traceback_message
        else:
            cur.close()
            return task_status_record


def init_psql_db_connection(psql_host=PSQL_HOST,
                            psql_port=PSQL_PORT,
                            psql_user=PSQL_USER,
                            psql_pass=PSQL_PASS,
                            psql_db=PSQL_DB):
    # type: (str,int,str,str,str)->connection
    return psycopg2.connect(database=psql_db, user=psql_user, password=psql_pass, host=psql_host, port=psql_port)


def backend_job(backend_db_handler:PgBackendDbHandler,
                document_object:DocumentObject,
                seq_document_sub_id:List[str],
                task_id:str,
                is_use_jumanpp:bool,
                is_normalize_text: bool = True,
                max_timeout:int=120)->bool:
    """* What you can do
    - レコードを1つ取得
    - レコードをKNPで解析
    - 解析ずみレコードを保存
    """
    if is_use_jumanpp:
        juman_command = JUMANPP_COMMAND
    else:
        juman_command = JUMAN_COMMAND

    try:
        knp_process_handler = KnpSubProcess(knp_command=KNP_COMMAND,
                                            juman_command=juman_command,
                                            juman_options=None,
                                            knp_options=None,
                                            process_mode='subprocess',
                                            path_juman_rc=None,
                                            eos_pattern="EOS",
                                            is_use_jumanpp=is_use_jumanpp,
                                            timeout_second=max_timeout)
    except:
        res_update = backend_db_handler.update_task_status_record(task_id=task_id,
                                                                  task_status=TASK_STATUS["FAILURE"],
                                                                  description="Failed to initialize Juman/KNP process",
                                                                  time_at=datetime.now())
        return False
    else:
        pass

    record_id, t_parsed_result = func_run_parsing(knp_process_handler=knp_process_handler,
                                                  record_id=document_object.record_id,
                                                  input_text=document_object.text,
                                                  is_normalize_text=is_normalize_text)
    document_object.set_knp_parsed_result(t_parsed_result)
    assert isinstance(document_object, DocumentObject)
    is_success_result = backend_db_handler.insert_knp_result_record(
        task_id=task_id,
        sentence_index=document_object.sentence_index,
        text_id=document_object.sub_id,
        knp_result=document_object.parsed_result,
        status=document_object.is_success,
        created_at=datetime.now())
    if is_success_result is False:
        backend_db_handler.update_task_status_record(task_id=task_id, task_status=TASK_STATUS['FAILURE'], description=traceback.format_exc(), time_at=datetime.now())
    else:
        pass

    is_task_done = backend_db_handler.is_task_done(task_id=task_id, seq_document_sub_id=seq_document_sub_id)
    if is_task_done:
        backend_db_handler.update_task_status_record(task_id=task_id, task_status=TASK_STATUS['DONE'],
                                                     time_at=datetime.now())
    else:
        return True


def check_input_document(document_obj:Dict[str,Any])->bool:
    """* What you can do
    """
    if not 'text-id' in document_obj:
        return False
    elif not 'text' in document_obj:
        return False
    elif not isinstance(document_obj['text-id'], str):
        return False
    elif not isinstance(document_obj['text'], str):
        return False
    else:
        return True


@flask_app.route('/')
def index():
    try:
        package_version = pkg_resources.get_distribution("knp_job").version
    except:
        package_version = None
        # index.html をレンダリングする
    return render_template('index.html', version_info=package_version)


@flask_app.route('/task_status/<task_id>', methods=['Get'])
def get_task_status(task_id:str):
    """* What you can do
    """
    try:
        db_connection = init_psql_db_connection()
        backend_handler = PgBackendDbHandler(db_connection)
    except:
        error_message = 'Failed to initialize DB connection!'
        response_body = {'message': 'Internal server error.',
                         'traceback': traceback.format_exc()}
        flask_app.logger.error(error_message)
        return jsonify(response_body), 500
    else:
        pass

    task_status_record = backend_handler.get_task_status(task_id)
    if task_status_record is None:
        error_message = 'No task named = {}'.format(task_id)
        response_body = {'message': error_message,
                         'traceback': traceback.format_exc()}
        flask_app.logger.error(error_message)
        return jsonify(response_body), 500
    else:
        return jsonify(task_status_record), 200


@flask_app.route('/run_knp_api', methods=['POST', 'Get'])
def run_knp_api():
    """* What you can do
    - It starts knp parsing job.

    * Format
    - body json must have following fields
        - input_document
            - text-id
            - text
        - is_use_jumanpp
        - n_jobs
        - is_split_text

    * Example
    >>> {"documents": [{"text-id": "input-1", "text": "東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"}]}
    """
    error_response_body = {'message': 'Internal server error.',
                           'traceback': None}
    if request.method == 'GET':
        return render_template('index.html')

    try:
        db_connection = init_psql_db_connection()
        backend_handler = PgBackendDbHandler(db_connection)
        task_id_result = backend_handler.insert_task_status_record()
    except:
        error_message = 'Failed to initialize DB connection!'
        error_response_body['message'] = error_message
        error_response_body['traceback'] = traceback.format_exc()
        flask_app.logger.error(error_message)
        return jsonify(error_response_body), 500
    else:
        if task_id_result[0] is False:
            error_message = 'Failed to initialize the task.'
            error_response_body['message'] = error_message
            error_response_body['traceback'] = task_id_result[1]
            flask_app.logger.error(error_message)
            return jsonify(error_response_body), 500
        else:
            task_id = task_id_result[1]

    body_object = request.get_json()
    input_document = body_object['documents']
    if not 'documents' in  body_object:
        error_message = 'Your input request-body does not have documents field.'
        error_response_body['message'] = error_message
        flask_app.logger.error(error_message)
        return jsonify(error_response_body), 500

    if False in [check_input_document(doc) for doc in input_document]:
        error_message = 'Your input document is not correct format.'
        error_response_body['message'] = error_message
        flask_app.logger.error(error_message)
        return jsonify(error_response_body), 500

    try:
        if 'n_jobs' in body_object:
            n_max_worker = body_object['n_jobs']
        else:
            n_max_worker = None

        if 'is_use_jumanpp' in body_object:
            is_use_jumanpp = body_object['is_use_jumanpp']
        else:
            is_use_jumanpp = False

        if 'is_split_text' in body_object:
            is_split_text = body_object['is_split_text']
        else:
            is_split_text = False
    except:
        error_message = traceback.format_exc()
        error_response_body['message'] = error_message
        flask_app.logger.error(error_message)
        return error_response_body
    else:
        pass

    if is_split_text:
        seq_doc_obj = generate_record_data_model_obj(input_document, is_split_sentence=True)
    else:
        seq_doc_obj = generate_document_objects(input_document)

    res_update = backend_handler.update_task_status_record(task_id=task_id, task_status=TASK_STATUS['PROGRESS'], time_at=datetime.now())
    try:
        # 非同期、かつThreadでタスクを開始する #
        seq_doc_sub_id = [doc_obj.sub_id for doc_obj in seq_doc_obj]
        with ThreadPoolExecutor(max_workers=n_max_worker) as executor:
            futures = [executor.submit(backend_job,
                                       backend_handler,
                                       doc_obj,
                                       seq_doc_sub_id,
                                       task_id,
                                       is_use_jumanpp,
                                       True,
                                       120) for doc_obj in seq_doc_obj]

        response_body = {'message': 'Your task is under processing.', 'task_id': task_id}
        return jsonify(response_body), 202, {'Location': url_for('get_task_status', task_id=task_id)}
    except:
        response_body = {'message': 'Internal server error.',
                         'traceback': traceback.format_exc()}
        return jsonify(response_body), 500


@flask_app.route('/get_result_api/<task_id>', methods=['GET'])
def get_result_api(task_id:str):
    """* What you can do
    - It gets knp-parsed result from local-DB

    * Format
    - body json must have following fields
        - text_ids
    >>> {"text-ids" : ["input-1", "input-2"]}
    """
    response_body = {'message': 'Internal server error.',
                     'traceback': None}
    try:
        db_connection = init_psql_db_connection()
        backend_handler = PgBackendDbHandler(db_connection)
    except:
        error_message = 'Failed to initialize DB connection!'
        response_body['message'] = error_message
        flask_app.logger.error(error_message)
        return jsonify(response_body), 500
    else:
        seq_parsed_document = backend_handler.get_processed_documents(task_id=task_id)
        if isinstance(seq_parsed_document, str):
            error_message = 'Failed to get parsed document from DB.'
            response_body['message'] = error_message
            response_body['traceback'] = seq_parsed_document
            return jsonify(response_body), 500
        else:
            pass

    try:
        response_body = {
            'parsed_documents': seq_parsed_document
        }
        return jsonify(response_body), 200
    except:
        response_body = {'message': 'Internal server error.',
                         'traceback': traceback.format_exc()}
        return jsonify(response_body), 500


if __name__ == '__main__':
    flask_app.debug = True # デバッグモード有効化
    try:
        check_db_connection = init_psql_db_connection()
        check_backend_handler = PgBackendDbHandler(check_db_connection)
    except:
        flask_app.logger.error("Failed to initialize connection into backend DB.")
        raise Exception("Failed to initialize connection into backend DB.")

    flask_app.run(host='0.0.0.0') # どこからでもアクセス可能に

