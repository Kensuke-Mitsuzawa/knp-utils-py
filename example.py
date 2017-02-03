from knp_utils import knp_job, models

argument_param = models.Params(
    knp_command='/usr/local/bin/knp',
    juman_command='/usr/local/bin/juman'
)

input_document = [
    {"text-id": "input-1", "text": "東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
    {"text-id": "input-2", "text": "指値オペの実施は現在の金融政策「長短金利操作（イールドカーブ・コントロール、ＹＣＣ）」を開始した２０１６年９月以来、２度目となる。"},
    {"text-id": "input-3", "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
]

result_obj = knp_job.main(seq_input_dict_document=input_document, argument_params=argument_param, is_normalize_text=True)

import json
print(json.dumps(result_obj.to_dict(), ensure_ascii=False))
