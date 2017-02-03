#! -*- coding: utf-8 -*-
import six
try:
    import pyknp
except:
    import pip
    pip.main(['install', 'http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://lotus.kuee.kyoto-u.ac.jp/nl-resource/pyknp/pyknp-0.3.tar.gz&name=pyknp-0.3.tar.gz'])


from knp_utils import knp_job, models
from pyknp import KNP
import subprocess



### Speed-Performance ###
input_document = [
    {"text-id": "input-1",
     "text": "東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
    {"text-id": "input-2", "text": "指値オペの実施は現在の金融政策「長短金利操作（イールドカーブ・コントロール、ＹＣＣ）」を開始した２０１６年９月以来、２度目となる。"},
    {"text-id": "input-3",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-4",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-5",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-6",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-7",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-8",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-9",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-10",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-11",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-12",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-13",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-14",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-15",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-16",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-17",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-18",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-19",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-20",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-21",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-22",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-23",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
    {"text-id": "input-24",
     "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
]

argument_param = models.Params(
    knp_command='/usr/local/bin/knp',
    juman_command='/usr/local/bin/juman'
)
knp_obj = pyknp.KNP(command='/usr/local/bin/knp', jumancommand='/usr/local/bin/juman')


import time

start = time.time()
result_obj = knp_job.main(seq_input_dict_document=input_document, argument_params=argument_param, is_normalize_text=True)
elapsed_time = time.time() - start
print ("[knp-utils] elapsed_time:{0} [Sec]".format(elapsed_time))

start = time.time()
for text_obj in input_document:
    echo_ps = subprocess.Popen(['echo', text_obj['text']], stdout=subprocess.PIPE)
    echo_ps.wait()
    juman_ps = subprocess.Popen(['/usr/local/bin/juman'], stdout=subprocess.PIPE, stdin=echo_ps.stdout)
    juman_ps.wait()
    out = subprocess.check_output(['/usr/local/bin/knp', '-tab'], stdin=juman_ps.stdout)

elapsed_time = time.time() - start
print ("[Native KNP subprocess] elapsed_time:{0} [Sec]".format(elapsed_time))

start = time.time()
for text_obj in input_document:
    echo_ps = subprocess.Popen(['echo', text_obj['text']], stdout=subprocess.PIPE)
    juman_ps = subprocess.Popen(['/usr/local/bin/juman', '-C', 'localhost'], stdout=subprocess.PIPE, stdin=echo_ps.stdout)
    juman_ps.wait()
    out = subprocess.check_output(['/usr/local/bin/knp', '-tab', '-C', 'localhost'], stdin=juman_ps.stdout)
elapsed_time = time.time() - start
print ("[Native KNP server] elapsed_time:{0} [Sec]".format(elapsed_time))


start = time.time()
for text_obj in input_document:
    knp_obj.parse(sentence=text_obj['text'])
elapsed_time = time.time() - start
print ("[pyknp] elapsed_time:{0} [Sec]".format(elapsed_time))