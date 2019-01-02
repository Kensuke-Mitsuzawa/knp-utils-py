#! -*- coding: utf-8 -*-
from knp_utils import knp_job
from knp_utils.db_handlers import sqlite3_handler as db_handler
import copy
import unittest
import json
import os
import shutil
import six
from uuid import uuid4


class TestCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # procedures before tests are started. This code block is executed only once

        cls.db_file_name = 'model_database.sqlite3'
        if 'tests' in os.getcwd():
            cls.path_input_documents = './resources/input_sample.json'
            cls.path_work_dir = './resources'
        else:
            cls.path_input_documents = 'tests/resources/input_sample.json'
            cls.path_work_dir = 'tests/resources'

        with open(cls.path_input_documents, 'r') as f:
            cls.seq_docs = json.loads(f.read())


        if six.PY2:
            doc_command_string = "echo '' | {}".format('knp')
            command_check = os.system(doc_command_string)
            if command_check == 0:
                cls.path_knp = 'knp'
            else:
                raise Exception("No command at {}".format('knp'))
        else:
            if shutil.which('knp'):
                cls.path_knp = 'knp'
            else:
                raise Exception("No command at {}".format('knp'))

        if six.PY2:
            doc_command_string = "echo '' | {}".format('juman')
            command_check = os.system(doc_command_string)
            if command_check == 0:
                cls.path_juman = 'juman'
            else:
                raise Exception("No command at {}".format('juman'))
        else:
            if shutil.which('juman'):
                cls.path_juman = 'juman'
            else:
                raise Exception("No command at {}".format('juman'))


    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # procedures before every tests are started. This code block is executed every time
        pass

    def tearDown(self):
        # procedures after tests are finished. This code block is executed only once
        if os.path.exists(os.path.join(self.path_work_dir, self.db_file_name)):
            os.remove(os.path.join(self.path_work_dir, self.db_file_name))

    def test_initialize_text_db(self):
        """作業用DBを初期化する"""
        knp_job.initialize_text_db(knp_job.generate_document_objects(self.seq_docs),
                                   work_dir=self.path_work_dir,
                                   file_name=self.db_file_name)

    def test_parse_one_sentence(self):
        """"""
        self.test_initialize_text_db()
        handler = db_handler.Sqlite3Handler(os.path.join(self.path_work_dir, self.db_file_name))
        knp_job.parse_text_block(seq_record_id=[4],
                                 path_db_handler=os.path.join(self.path_work_dir, self.db_file_name),
                                 knp_command=self.path_juman,
                                 juman_command=self.path_juman)

    def test_parse_texts(self):
        self.test_initialize_text_db()
        knp_job.parse_texts(path_db_handler=os.path.join(self.path_work_dir, self.db_file_name),
                            n_jobs=2,
                            knp_command=self.path_knp,
                            juman_command=self.path_juman)

    def test_stress_test_pattern1(self):
        """大量の入力文を与えた場合の挙動をチェックする
        ### with normalization is True
        """
        seq_long_test_input = self.seq_docs * 20

        result_obj = knp_job.main(
            seq_input_dict_document=seq_long_test_input,
            is_normalize_text=True,
            n_jobs=-1
        )
        self.assertTrue(len(result_obj.seq_document_obj) == len(seq_long_test_input))

    def test_stress_test_pattern2(self):
        """大量の入力文を与えた場合の挙動をチェックする
        ### with normalization is False
        """
        seq_long_test_input = self.seq_docs * 20

        result_obj = knp_job.main(
            seq_input_dict_document=seq_long_test_input,
            is_normalize_text=False)
        self.assertTrue(len(result_obj.seq_document_obj) == len(seq_long_test_input))

    def test_exception_during_sentence(self):
        """KNPの解析結果文字列が例外を起こすときの処理"""
        seq_input = [
            {'text-id': 'test-1', 'text': 'ベッキー♪#も、なんかもう世代交代じゃね？'},
            {'text-id': 'test-2', 'text': 'ベッキー♪#も、なんかもう世代交代じゃね？'},
            {'text-id': 'test-3', 'text': 'ベッキー♪#も、なんかもう世代交代じゃね？'}
        ]

        result_obj = knp_job.main(
            seq_input_dict_document=seq_input,
            is_normalize_text=False,
            is_delete_working_db=True
        )

    def test_subprocess_mode(self):
        result = knp_job.main(self.seq_docs, is_normalize_text=True, n_jobs=1, process_mode='subprocess')

    def test_invalid_option_command(self):
        """不正なコマンド引数を与えた時のエラー発生をテスト"""
        seq_input = [
            {'text-id': 'test-1', 'text': 'ベッキー♪#も、なんかもう世代交代じゃね？'},
            {'text-id': 'test-2', 'text': 'ベッキー♪#も、なんかもう世代交代じゃね？'},
            {'text-id': 'test-3', 'text': 'ベッキー♪#も、なんかもう世代交代じゃね？'}
        ]

        with self.assertRaises(Exception):
            knp_job.main(seq_input_dict_document=seq_input,is_normalize_text=True,n_jobs=-1,juman_options='-LL',knp_options='-KK')

        with self.assertRaises(Exception):
            knp_job.main(seq_input_dict_document=seq_input,is_normalize_text=True,n_jobs=-1,knp_options='-KK')

    def test_input_document_with_args(self):
        """入力documentにargsが付属しているときの挙動をテスト"""
        seq_input_docs = copy.deepcopy(self.seq_docs)
        for doc in seq_input_docs:
            doc.update({"args": {"date": "2018/12/12"}})

        result_docs = knp_job.main(
            seq_input_dict_document=seq_input_docs,
            n_jobs=-1,
            is_normalize_text=True,
            is_split_text=True
        )
        for doc_obj in result_docs.seq_document_obj:
            assert doc_obj.document_args is not None
            assert isinstance(doc_obj.document_args, dict)
            assert "date" in doc_obj.document_args and doc_obj.document_args["date"] == "2018/12/12"


if __name__ == '__main__':
    unittest.main()