#! -*- coding: utf-8 -*-
from knp_utils import knp_job, models, KnpSubProcess, DocumentObject, ResultObject
import tempfile
import uuid
import argparse
import json
import os
import codecs
import six

parser = argparse.ArgumentParser(description='Python-based KNP utils tool.')
parser.add_argument('-i', '--path-input-json-path', required=True, help='Path into your input json file.')
parser.add_argument('-j', '--juman-command', required=False, default='/usr/local/bin/juman', help='Path to juman command.')
parser.add_argument('-k', '--knp-command', required=False, default='/usr/local/bin/knp', help='Path to knp command.')
parser.add_argument('--path-juman-rc', required=False, default=None, help='Path to juman rc file')
parser.add_argument('--process_mode', required=False, default="pexpect", help='A mode name to process data.')
parser.add_argument('--n-jobs', required=False, default=8, type=int, help='#Thread to run')
parser.add_argument('--working-dir', required=False, default=tempfile.mkdtemp())
parser.add_argument('--file-name', required=False, default=str(uuid.uuid4()))
parser.add_argument('--is-delete-working-db', required=False, default=True, action='store_true')
parser.add_argument('--is-normalize-text', required=False, action='store_true', default=False)
"""
# sever mode is invalid now
parser.add_argument('--juman-server-host')
parser.add_argument('--juman-server-port')
parser.add_argument('--knp-server-host')
parser.add_argument('--knp-server-port')"""
args = parser.parse_args()

if not os.path.exists(args.path_input_json_path):
    raise Exception('There is no file at {}'.format(args.path_input_json_path))
else:
    if six.PY2:
        with codecs.open(args.path_input_json_path, 'r', 'utf-8') as f:
            seq_input_dict_document = json.loads(f.read())
    else:
        with open(args.path_input_json_path, 'r') as f:
            seq_input_dict_document = json.loads(f.read())


result_obj = knp_job.main(
    seq_input_dict_document=seq_input_dict_document,
    n_jobs=args.n_jobs,
    knp_command=args.knp_command,
    juman_command=args.juman_command,
    path_juman_rc=args.path_juman_rc,
    process_mode=args.process_mode,
    work_dir=args.working_dir,
    file_name=args.file_name,
    is_delete_working_db=args.is_delete_working_db,
    is_normalize_text=args.is_normalize_text
)

if six.PY2:
    print(json.dumps(result_obj.to_dict(), ensure_ascii=True))
else:
    print(json.dumps(result_obj.to_dict(), ensure_ascii=False))