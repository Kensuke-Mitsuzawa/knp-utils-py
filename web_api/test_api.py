#! -*- coding: utf-8 -*-
from web_api.app import flask_app

# else
import unittest
import json
import os
import time


class TestV1Application(unittest.TestCase):
    """V1アプリケーションのテストを実施する"""
    @classmethod
    def setUpClass(cls):
        cls.flask_app = flask_app.test_client()

    @classmethod
    def tearDownClass(cls):
        pass

    def generate_test_data(self):
        return [
            {"text-id": "example-0", "text": "東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
            {"text-id": "example-1", "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
            {"text-id": "example-2", "text": "「妹キャラ」「ロリフェイス」で絶大な人気を誇るAV女優・紗倉まな。バカリズム、宮川大輔、おぎやはぎの小木ら芸人にもファンが多いことで知られる紗倉が、自伝的エッセイ『高専生だった私が出会った世界でたった一つの天職』（宝島社）を出版し話題を呼んでいる。"}
        ]

    def test_root(self):
        """ルートページテスト"""
        response = self.flask_app.get('/')
        self.assertTrue(response.status_code == 200)

    def test_api_post_start_job(self):
        """knpパーズjobの開始テスト。202が返却されれば、ok
        """
        test_data = self.generate_test_data()
        # case-1 成功 #
        response_data = self.flask_app.post('/run_knp_api',
                                            data=json.dumps({"documents":test_data}),
                                            content_type='application/json')
        self.assertTrue(response_data.status_code == 202)
        response_body = json.loads(response_data.data.decode('utf-8'))
        self.assertTrue('task_id' in response_body)

        # case-2 documentsをわざとrequestに入れない #
        response_data = self.flask_app.post('/run_knp_api',
                                            data=json.dumps({}),
                                            content_type='application/json')
        self.assertTrue(response_data.status_code == 500)

        # case-3 documentsのデータ形式を不正にする #
        mistaken_data = [
            {"id": 0, "data": "東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
        ]
        response_data = self.flask_app.post('/run_knp_api',
                                            data=json.dumps({"documents": mistaken_data}),
                                            content_type='application/json')
        self.assertTrue(response_data.status_code == 500)

    def test_api_get_result_job(self):
        """api_get_result_jobのテスト。"""
        test_data = self.generate_test_data()
        # case-1 成功 #
        response_data = self.flask_app.post('/run_knp_api',
                                            data=json.dumps({"documents":test_data}),
                                            content_type='application/json')
        self.assertTrue(response_data.status_code == 202)
        response_body = json.loads(response_data.data.decode('utf-8'))
        self.assertTrue('task_id' in response_body)
        task_id = response_body['task_id']
        ## job終了まで待機 ##
        while True:
            job_status_response = self.flask_app.get(os.path.join('/task_status/', task_id))
            if not job_status_response.status_code == 200:
                raise Exception('/task_status/ is NOT working correctly!')
            if json.loads(job_status_response.data.decode('utf-8'))['task_status']=='DONE':
                break
            else:
                time.sleep(3)
        ## 終了ずみレコードの取得 ##
        processed_record_response = self.flask_app.get(os.path.join('/get_result_api', task_id))
        self.assertTrue(processed_record_response.status_code == 200)
        response_body = json.loads(processed_record_response.data.decode('utf-8'))
        self.assertTrue('parsed_documents' in response_body)


if __name__ == '__main__':
    unittest.main()