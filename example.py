#! -*- coding: utf-8 -*-
from knp_utils import knp_job, models
import six

argument_param = models.Params(
    n_jobs=1,
    knp_command='/usr/local/bin/knp',
    juman_command='/usr/local/bin/juman'
)

if six.PY2:
    input_document = [
        {u"text-id": u"input-1", u"text": u"東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
        {u"text-id": u"input-2", u"text": u"指値オペの実施は現在の金融政策「長短金利操作（イールドカーブ・コントロール、ＹＣＣ）」を開始した２０１６年９月以来、２度目となる。"},
        {u"text-id": u"input-3", u"text": u"ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    ]
else:
    input_document = [
        {"text-id": "input-1", "text": "東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
        {"text-id": "input-2", "text": "指値オペの実施は現在の金融政策「長短金利操作（イールドカーブ・コントロール、ＹＣＣ）」を開始した２０１６年９月以来、２度目となる。"},
        {"text-id": "input-3", "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    ]

result_obj = knp_job.main(seq_input_dict_document=input_document, argument_params=argument_param, is_normalize_text=True)

import json
print(json.dumps(result_obj.to_dict(), ensure_ascii=False))


### With pyknp
try:
    import pyknp
except:
    import pip
    pip.main(['install', 'http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://lotus.kuee.kyoto-u.ac.jp/nl-resource/pyknp/pyknp-0.3.tar.gz&name=pyknp-0.3.tar.gz'])
else:
    from pyknp import KNP
    knp_obj = KNP()
    for knp_parsed_obj in result_obj.seq_document_obj:
        pyknp_parsed_result = knp_obj.result(input_str=knp_parsed_obj.parsed_result)
        bnst_surface = ["".join(mrph.midasi for mrph in bnst_obj.mrph_list()) for bnst_obj in pyknp_parsed_result.bnst_list()]
        print(bnst_surface)