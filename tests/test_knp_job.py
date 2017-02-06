from knp_utils import knp_job
from knp_utils.models import  Params
from knp_utils import db_handler
import unittest
import json
import os


class TestCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # procedures before tests are started. This code block is executed only once
        cls.path_work_dir = './resources'
        cls.db_file_name = 'model_database.sqlite3'
        cls.path_input_documents = './resources/input_sample.json'
        with open(cls.path_input_documents, 'r') as f:
            cls.seq_docs = json.loads(f.read())

        cls.path_knp = '/usr/local/bin/knp'
        cls.path_juman = '/usr/local/bin/juman'

        cls.param_argument = Params(knp_command=cls.path_knp,
                                    juman_command=cls.path_juman)


    @classmethod
    def tearDownClass(cls):
        # procedures after tests are finished. This code block is executed only once
        if os.path.exists(os.path.join(cls.path_work_dir, cls.db_file_name)):
            os.remove(os.path.join(cls.path_work_dir, cls.db_file_name))

    def setUp(self):
        # procedures before every tests are started. This code block is executed every time
        pass

    def tearDown(self):
        # procedures after every tests are finished. This code block is executed every time
        pass

    def test_initialize_text_db(self):
        """作業用DBを初期化する"""
        knp_job.initialize_text_db(knp_job.generate_document_objects(self.seq_docs),
                                   work_dir=self.path_work_dir, file_name=self.db_file_name)

    def test_parse_one_sentence(self):
        """"""
        self.test_initialize_text_db()
        handler = db_handler.Sqlite3Handler(os.path.join(self.path_work_dir, self.db_file_name))
        knp_job.parse_one_text(record_id=4,
                               path_sqlite3_db_handler=os.path.join(self.path_work_dir, self.db_file_name),
                               argument_params=self.param_argument)

    def test_parse_texts(self):
        self.test_initialize_text_db()
        knp_job.parse_texts(path_sqlite3_db_handler=os.path.join(self.path_work_dir, self.db_file_name),
                            argument_params=self.param_argument)


if __name__ == '__main__':
    unittest.main()