#! -*- coding: utf-8 -*-
from knp_utils.models import KnpSubProcess, DocumentObject
# else
from typing import List, Tuple, Dict, Any, Callable, Iterator
import re
import jaconv
import six
import os
from six import text_type, PY2, PY3


def func_normalize_text(text):
    # type: (str)->str
    """* What you can do
    - It make normalize input text into text which is suitable to KNP analysis.
    """
    if six.PY2:
        if isinstance(text, str):
            text = text.decode('utf-8')
        return jaconv.h2z(text=re.sub(r'\s', '', string=text), kana=True, ascii=True, digit=True)
    else:
        return jaconv.h2z(text=re.sub(r'\s', '', string=text), kana=True, ascii=True, digit=True)


def __check_dict_document(dict_object):
    # type: (Dict[str,List[str]])->bool
    """* What you can do
    - It checks if document is correct or Not
    """
    if not "text" in dict_object:
        raise Exception("Your input does not have key = 'text'")
    if not "text-id" in dict_object:
        raise Exception("Your input does not have key = 'text-id'")

    return True


def __split_sentence_py3(text):
    # type: (str)->List[Tuple[int,str]]
    eos_pattern = re.compile("(?P<mark>[。|！|？|\u2753|\u2757|\u2049|\n]+)")
    particle_pattern = re.compile("(?P<mark>[！|？|\u2753|\u2757|\u2049]+)[$$]+(?P<particle>[が|を|に|と|の|で|や|って])")
    bracket_pattern = re.compile("(?P<quote>「.*?」|『.*?』|（.*?）)")
    start_mark_pattern = re.compile("(?P<mark>[\u2010-\u266F])")
    break_pattern = re.compile("[$$]+")

    # 改行の削除
    # ただし、読点が投稿中に含まれない場合には、改行を文区切りとみなす
    if "。" not in text:
        pass
    else:
        text = text.replace("\n", "")

    # 文末と判断できる場合すべてに、区切り文字'$$'を挿入する
    # ただし、投稿の最後にもつけると空文ができるので、最後はrstripで落とす
    text = eos_pattern.sub("\g<mark>$$", text).rstrip("$")

    # 助詞（らしき文字列）が続く区切り文字を削除
    # 「じゃらんのアプリの勧誘？がウザい。」のような場合に区切らないため
    text = particle_pattern.sub("\g<mark>\g<particle>", text)

    # カッコ内に含まれる区切り文字を削除
    repl_func = lambda match_obj: match_obj.group("quote").replace("$$", "")
    text = bracket_pattern.sub(repl_func, text)

    # 記号ではじまる投稿は、箇条書き形式の場合であると仮定し、その記号の前にも区切り文字を挿入する
    if start_mark_pattern.match(text):
        text = start_mark_pattern.sub("$$\g<mark>", text).lstrip("$$")

    # 最終的に残った区切り文字で分割
    return [(sent_id, sentence.strip()) for sent_id, sentence in enumerate(break_pattern.split(text))]


def split_sentence(text):
    # type: (str)->List[Tuple[int,str]]
    """* What you can do
    - 文分割を実施する
    * Output
    - (文番号,分割済みテキスト)のタプル
    """
    if PY3:
        return __split_sentence_py3(text)
    elif PY2:
        if '。'.decode('utf-8') in text:
            __ = [t for t in text.split('。'.decode('utf-8')) if len(t) > 0]
            return [(i, t) for i, t in enumerate(__)]
        else:
            return [(0, text)]
    else:
        raise Exception()


def generate_record_data_model_obj(seq_input_obj,
                                   is_split_sentence):
    # type: (List[Dict[str,Any]], bool)->Iterator[DocumentObject]
    """* What you can do
    - 入力データをオブジェクト化してしまう。
    - 文単位管理の可能性があるので、不満用とオブジェクトと同じものを使う
    """
    seq_record_data_model = []
    record_id = 0
    for dict_document in seq_input_obj:
        __check_dict_document(dict_document)
        # ===========================================================================================================
        if is_split_sentence:
            """文分割の実施"""
            for tuple_sentid_text in split_sentence(dict_document['text']):
                sentence, sentence_index = tuple_sentid_text[1], tuple_sentid_text[0]
                args = dict_document['args'] if 'args' in dict_document else None
                record_data_model = DocumentObject(
                    record_id=record_id,
                    text=sentence,
                    status=False,
                    parsed_result=None,
                    sub_id=dict_document['text-id'],
                    sentence_index=sentence_index,
                    document_args=args
                )
                #seq_record_data_model.append(record_data_model)
                yield record_data_model
                record_id += 1
        else:
            """文分割は実施しない"""
            args = dict_document['args'] if 'args' in dict_document else None
            record_data_model = DocumentObject(
                record_id=record_id,
                text=dict_document['text'],
                status=False,
                parsed_result=None,
                sub_id=dict_document['text-id'],
                document_args=args
            )

            #seq_record_data_model.append(record_data_model)
            yield record_data_model
            record_id += 1
        # ===========================================================================================================
    #return seq_record_data_model


def generate_document_objects(seq_input_dict_document):
    # type: (List[Dict[str,Any]]) -> Iterator[DocumentObject]
    for index_id, dict_document in enumerate(seq_input_dict_document):
        __check_dict_document(dict_document)
        args = dict_document['args'] if 'args' in dict_document else None
        _d = DocumentObject(
            record_id=index_id,
            sentence_index=0,
            text=dict_document['text'],
            status=False,
            parsed_result=None,
            sub_id=dict_document['text-id'],
            document_args=args)
        yield _d


def func_run_parsing(knp_process_handler,
                     record_id,
                     input_text,
                     is_normalize_text,
                     func_normalization=func_normalize_text):
    # type: (KnpSubProcess,text_type,text_type,bool,Callable)->Tuple[text_type,Tuple[bool,text_type]]
    """It starts parsing-process with KNP.
    This function is designed to work in separate. Thus, you're able to call the function from Thread if you like.
    """
    if is_normalize_text:
        text = func_normalization(input_text)
    else:
        text = input_text
    parsed_result = knp_process_handler.run_command(text=text)  # type: Tuple[bool,six.text_type]

    return record_id, parsed_result