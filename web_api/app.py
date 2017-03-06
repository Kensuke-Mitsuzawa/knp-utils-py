#! -*- coding: utf-8 -*-
## flask package
from flask import Flask, render_template, request, redirect, url_for, jsonify
## typing
from typing import List, Dict, Any, Union
## knp_utils
from knp_utils import knp_job, models, db_handler
## celery
from celery import Celery
## to generate job-queue-id
import uuid
## to save job result
# else
import pkg_resources
import os
import traceback
import json
import apsw
from datetime import datetime


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


flask_app = Flask(__name__)
############ You change following config depending on your app ############
flask_app.config.from_object('config.DevelopmentConfig')
flask_app.config.from_object('celeryconfig')
flask_app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379')
celery = make_celery(flask_app)

### Connect with backend DB
path_backend_db = os.path.join(flask_app.config['PATH_WORKING_DIR'], flask_app.config['FILENAME_BACKEND_SQLITE3'])
KNP_COMMAND=flask_app.config['KNP_COMMAND']
JUMAN_COMMAND=flask_app.config['JUMAN_COMMAND']
JUMANPP_SERVER_HOST=flask_app.config['JUMANPP_SERVER_HOST']
JUMANPP_SERVER_PORT=flask_app.config['JUMANPP_SERVER_PORT']


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
        handler = db_handler.Sqlite3Handler(path_sqlite_file=path_backend_db)
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