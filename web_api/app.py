#! -*- coding: utf-8 -*-
## flask package
from flask import Flask, render_template, request, redirect, url_for, jsonify
## typing
from typing import List, Dict, Any, Union, Tuple
## knp_utils
from knp_utils import knp_job, models, db_handler
## to generate job-queue-id
import uuid
## postgresql
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
import psycopg2
# else
import pkg_resources
import os
import traceback
from threading import Thread
from datetime import datetime

'''
def make_celery(app):
    celery = Celery('app',
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
    '''


flask_app = Flask(__name__)
'''
############ You change following config depending on your app ############
flask_app.config.from_object('config.DevelopmentConfig')
flask_app.config.from_object('celeryconfig')
flask_app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379')
celery = make_celery(flask_app)
'''

### Connect with backend DB
temporary_worker_db = os.path.join(flask_app.config['PATH_WORKING_DIR'], flask_app.config['FILENAME_BACKEND_SQLITE3'])
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

#JUMANPP_SERVER_HOST=flask_app.config['JUMANPP_SERVER_HOST']
#JUMANPP_SERVER_PORT=flask_app.config['JUMANPP_SERVER_PORT']

'''
@celery.task(bind=True)
def knp_job_main(self,
                 input_document:List[Dict[str,Any]],
                 n_jobs:int,
                 is_use_jumanpp:bool
                 )->models.ResultObject:
    """* What you can do"""
    started_at = datetime.now()
    self.update_state(state='PROGRESS', meta={'started_at': started_at.strftime('%Y-%m-%d %H:%M:%S')})

    if is_use_jumanpp:
        argument_param = models.Params(
            n_jobs=n_jobs,
            knp_command=KNP_COMMAND,
            juman_command=JUMAN_COMMAND,
            juman_server_host=JUMANPP_SERVER_HOST,
            juman_server_port=JUMANPP_SERVER_PORT,
            is_use_jumanpp=is_use_jumanpp)
    else:
        argument_param = models.Params(
            n_jobs=n_jobs,
            knp_command=KNP_COMMAND,
            juman_command=JUMAN_COMMAND,
            is_use_jumanpp=is_use_jumanpp)

    keys_document = [doc_obj['text-id'] for doc_obj in input_document]
    knp_job.main(seq_input_dict_document=input_document,
                              argument_params=argument_param,
                              work_dir=flask_app.config['PATH_WORKING_DIR'],
                              file_name=flask_app.config['FILENAME_BACKEND_SQLITE3'],
                              is_normalize_text=True,
                              is_get_processed_doc=True,
                              is_delete_working_db=False)
    return {'status': 'completed',
            'documents-keys': keys_document,
            'started_at': started_at.strftime('%Y-%m-%d %H:%M:%S')}
            '''

TASK_STATUS = {
    'PENDING': 'PENDING',
    'FAILURE': 'FAILURE',
    'PROGRESS': 'PROGRESS',
    'DONE': 'DONE'
}


class PgBackendDbHandler(object):
    def __init__(self, db_connection, table_knp_result='knp_result', table_task_status='task_status'):
        # type: (connection, str, str)->None
        self.db_connection = db_connection
        self.table_knp_result = table_knp_result
        self.table_task_status = table_task_status

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

        cur = self.db_connection.cursor()  # type: cursor
        try:
            cur.execute(sql_insert, (task_id, task_status, description, created_at, updated_at))
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
                                 sent_id,
                                 text_id,
                                 knp_result,
                                 status,
                                 created_at):
        """"""
        # type: (str,str,str,str,bool,datetime)->Union[str,bool]
        sql_insert = "INSERT INTO {} (sent_id,text_id,task_id,knp_result,status,created_at) VALUES (%s,%s,%s,%s,%s,%s)".format(self.table_knp_result)
        cur = self.db_connection.cursor()  # type: cursor
        try:
            cur.execute(sql_insert, (sent_id, text_id, task_id, knp_result, status, created_at))
            self.db_connection.commit()
        except:
            traceback_message = traceback.format_exc()
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





def init_psql_db_connection(psql_host=PSQL_HOST,
                            psql_port=PSQL_PORT,
                            psql_user=PSQL_USER,
                            psql_pass=PSQL_PASS,
                            psql_db=PSQL_DB):
    # type: (str,int,str,str,str)->connection
    return psycopg2.connect(database=psql_db, user=psql_user, password=psql_pass, host=psql_host, port=psql_port)



def backend_job(backend_db_handler:PgBackendDbHandler,
                input_document:List[Dict[str,Any]],
                n_jobs:int,
                is_use_jumanpp:bool):
    """"""
    started_at = datetime.now()

    if is_use_jumanpp:
        argument_param = models.Params(
            knp_command=KNP_COMMAND,
            juman_command=JUMANPP_COMMAND,
            is_use_jumanpp=True,
            process_mode=''
        )
    else:
        argument_param = models.Params(
            n_jobs=n_jobs,
            knp_command=KNP_COMMAND,
            juman_command=JUMAN_COMMAND,
            is_use_jumanpp=is_use_jumanpp)

    keys_document = [doc_obj['text-id'] for doc_obj in input_document]
    knp_job.main(seq_input_dict_document=input_document,
                              argument_params=argument_param,
                              work_dir=flask_app.config['PATH_WORKING_DIR'],
                              file_name=flask_app.config['FILENAME_BACKEND_SQLITE3'],
                              is_normalize_text=True,
                              is_get_processed_doc=True,
                              is_delete_working_db=False)
    return {'status': 'completed',
            'documents-keys': keys_document,
            'started_at': started_at.strftime('%Y-%m-%d %H:%M:%S')}


@flask_app.route('/')
def index():
    try:
        package_version = pkg_resources.get_distribution("knp_job").version
    except:
        package_version = None
        # index.html をレンダリングする
    return render_template('index.html', version_info=package_version)


@flask_app.route('/status/<task_id>', methods=['Get'])
def taskstatus(task_id):
    task = knp_job_main.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'started_at': task.info.get('started_at'),
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'started_at': task.info.get('started_at'),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'started_at': task.info.get('started_at'),
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


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
    >>> {"input_document": [{"text-id": "input-1", "text": "東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"}]}
    """
    if request.method == 'GET':
        return render_template('index.html')

    body_object = request.get_json()
    try:
        input_document = body_object['input_document']
        n_jobs = body_object['n_jobs']
        is_use_jumanpp = body_object['is_use_jumanpp']
        text_ids = [doc_obj['text-id'] for doc_obj in input_document]

        # todo ここをタスク開始命令に変更
        task = knp_job_main.apply_async(args=[input_document, n_jobs, is_use_jumanpp])
        response_body = {'message': 'your job is started',
                         'text_ids': text_ids,
                         'task_id': task.id}
        return jsonify(response_body), 202, {'Location': url_for('taskstatus', task_id=task.id)}
    except:
        response_body = {'message': 'Internal server error.',
                         'traceback': traceback.format_exc()}
        return jsonify(response_body), 500


@flask_app.route('/get_result_api', methods=['POST', 'GET'])
def get_result_api():
    """* What you can do
    - It gets knp-parsed result from local-DB

    * Format
    - body json must have following fields
        - text_ids
    >>> {"text-ids" : ["input-1", "input-2"]}
    """
    try:
        body_object = request.get_json()
        seq_text_ids = body_object['text-ids']
        handler = db_handler.Sqlite3Handler(path_sqlite_file=temporary_worker_db)
        seq_document_object = [None] * len(seq_text_ids)
        for i, text_id in enumerate(seq_text_ids):
                seq_document_object[i] = handler.get_one_record_sub_id(text_id).to_dict()

        response_body = {
            'text_ids': seq_text_ids,
            'result': seq_document_object
        }
        return jsonify(response_body), 200
    except:
        response_body = {'message': 'Internal server error.',
                         'traceback': traceback.format_exc()}
        return jsonify(response_body), 500


if __name__ == '__main__':
    flask_app.debug = True # デバッグモード有効化
    flask_app.run(host='0.0.0.0') # どこからでもアクセス可能に