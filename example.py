#! -*- coding: utf-8 -*-
from knp_utils import knp_job, models, KnpSubProcess
import six
import logging
logger = logging.getLogger('command')


#PATH_JUMAN_COMMAND="/usr/local/bin/juman"
#PATH_JUMAN_COMMAND="/usr/local/bin/jumanpp"
#PATH_KNP_COMMAND="/usr/local/bin/knp"
PATH_JUMAN_COMMAND="juman"
PATH_KNP_COMMAND="knp"
PATH_JUMANPP_COMMAND="jumanpp"


def example_interface():
    """This functions shows you how to use interface function"""
    if six.PY2:
        input_document = [
            {u"text-id": u"input-1", u"text": "おじいさんは山に芝刈りへ、おばあさんは川に洗濯へ行きました。"},
            {u"text-id": u"input-2", u"text": u"東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
            {u"text-id": u"input-3", u"text": u"指値オペの実施は現在の金融政策「長短金利操作（イールドカーブ・コントロール、ＹＣＣ）」を開始した２０１６年９月以来、２度目となる。"},
            {u"text-id": u"input-4", u"text": u"ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
        ]
    else:
        input_document = [
            {"text-id": "input-1","text": "おじいさんは山に芝刈りへ、おばあさんは川に洗濯へ行きました。"},
            {"text-id": "input-2", "text": "東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
            {"text-id": "input-3", "text": "指値オペの実施は現在の金融政策「長短金利操作（イールドカーブ・コントロール、ＹＣＣ）」を開始した２０１６年９月以来、２度目となる。"},
            {"text-id": "input-4", "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
        ]

    result_obj = knp_job.main(seq_input_dict_document=input_document,
                              n_jobs=-1,
                              is_normalize_text=True,
                              is_get_processed_doc=True,
                              is_split_text=True,
                              juman_command=PATH_JUMAN_COMMAND,  # Note: You can set jumanpp also (if it's available in your system)
                              knp_command=PATH_KNP_COMMAND,
                              process_mode="pexpect")

    import json
    logger.info(msg="--- example of parsed result ---")
    print(json.dumps(result_obj.to_dict()[0], ensure_ascii=False))
    logger.info('---')

    """You call get associated with pyknp which is official python wrapper for KNP"""
    ### With pyknp
    try:
        import pyknp
    except:
        logger.error(msg="Failed to install pyknp. Skip this process.")
    else:
        from pyknp import KNP
        knp_obj = KNP()
        for knp_parsed_obj in result_obj.seq_document_obj:
            pyknp_parsed_result = knp_obj.result(input_str=knp_parsed_obj.parsed_result)
            bnst_surface = ["".join(mrph.midasi for mrph in bnst_obj.mrph_list()) for bnst_obj in pyknp_parsed_result.bnst_list()]
            print(bnst_surface)


def performance_comparison():
    """This function shows you comparison of processing speed"""
    if six.PY2:
        input_document = [
            {u"text-id": u"input-1", u"text": "おじいさんは山に芝刈りへ、おばあさんは川に洗濯へ行きました。"},
            {u"text-id": u"input-2", u"text": u"東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
            {u"text-id": u"input-3", u"text": u"指値オペの実施は現在の金融政策「長短金利操作（イールドカーブ・コントロール、ＹＣＣ）」を開始した２０１６年９月以来、２度目となる。"},
            {u"text-id": u"input-4", u"text": u"ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
        ] * 10
    else:
        input_document = [
            {"text-id": "input-1","text": "おじいさんは山に芝刈りへ、おばあさんは川に洗濯へ行きました。"},
            {"text-id": "input-2", "text": "東京　３日　ロイター］ - 日銀は３日、急激な金利上昇を止めるため、特定の年限の国債買い入れを増やす「指値オペ」を実施した。トランプ米大統領による円安誘導批判を受け、日銀が長期金利を押し下げるようなオペは難しくなるとの思惑が浮上。長期金利は３日、一時、０．１５％を超えて上昇した。日銀は、指し値オペの実行によってゼロ％に抑える政策に変化がないことを明確にし、圧力を意識した市場に「強い意思」を示した格好だ。"},
            {"text-id": "input-3", "text": "指値オペの実施は現在の金融政策「長短金利操作（イールドカーブ・コントロール、ＹＣＣ）」を開始した２０１６年９月以来、２度目となる。"},
            {"text-id": "input-4", "text": "ドナルド・トランプ米大統領が有権者の心をつかんだ理由の一つは、その率直な物言いだ。ドルに関して言えば、米国の歴代財務長官が昔から繰り返してきた「強いドルは米国の国益にかなう」という妄言と決別するという新政権の意向は歓迎されよう。"},
        ] * 10
    import time
    ## process_mode is pexpect(multi-thread, keep running processes) ##
    start = time.time()
    knp_job.main(seq_input_dict_document=input_document,
                 n_jobs=-1,
                 process_mode='pexpect',
                 is_normalize_text=True,
                 is_get_processed_doc=True,
                 juman_command=PATH_JUMAN_COMMAND,
                 knp_command=PATH_KNP_COMMAND)
    elapsed_time = time.time() - start
    print("pexpect mode, finished with :{0}".format(elapsed_time) + "[sec]")

    ## process_mode is everytime(multi-thread, launch processes everytime you call) ##
    start = time.time()
    knp_job.main(seq_input_dict_document=input_document,
                 n_jobs=-1,
                 process_mode='everytime',
                 is_normalize_text=True,
                 is_get_processed_doc=True,
                 juman_command=PATH_JUMAN_COMMAND,
                 knp_command=PATH_KNP_COMMAND)
    elapsed_time = time.time() - start
    print("everytime mode, finished with :{0}".format(elapsed_time) + "[sec]")

    ## pyknp which is official KNP wrapper ##
    ### With pyknp
    try:
        import pyknp
    except:
        logger.error(msg="Failed to install pyknp. Skip this process.")
    else:
        start = time.time()
        from pyknp import KNP
        knp_obj = KNP(command=PATH_KNP_COMMAND, jumancommand=PATH_JUMAN_COMMAND, jumanpp=True)
        for document_obj in input_document:
            knp_obj.knp(sentence=knp_job.func_normalize_text(document_obj['text']))
        elapsed_time = time.time() - start
        print("pyknp, finished with :{0}".format(elapsed_time) + "[sec]")


if __name__=='__main__':
    example_interface()
    performance_comparison()
