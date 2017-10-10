#! -*- coding: utf-8 -*-
from knp_utils.models import KnpSubProcess
# else
from typing import List, Tuple, Dict, Any, Callable
import re
import jaconv
import six
import os
from six import text_type


def func_normalize_text(text):
    """* What you can do
    - It make normalize input text into text which is suitable to KNP analysis.
    """
    # type: (str)->str
    if six.PY2:
        if isinstance(text, str):
            text = text.decode('utf-8')
        return jaconv.h2z(text=re.sub(r'\s', '', string=text), kana=True, ascii=True, digit=True)
    else:
        return jaconv.h2z(text=re.sub(r'\s', '', string=text), kana=True, ascii=True, digit=True)


def func_run_parsing(input_text,
                     knp_command='/usr/local/bin/knp',
                     juman_command='/usr/local/bin/juman',
                     knp_options=None,
                     juman_options=None,
                     process_mode='subprocess',
                     path_juman_rc=None,
                     is_normalize_text=False,
                     timeout_seconds=60,
                     func_normalization=func_normalize_text):
    """* What you can do
    - It starts parsing-process with KNP.
    - This function is designed to work in separate. Thus, you're able to call the function from Thread if you like.
    """
    # type: (text_type,text_type,text_type,text_type,text_type,text_type,text_type,bool,int,Callable)->text_type
    if os.path.basename(juman_command)=='jumanpp':
        is_use_jumanpp = True
    else:
        is_use_jumanpp = False

    if is_normalize_text:
        text = func_normalization(input_text)
    else:
        text = input_text

    knp_process_handler = KnpSubProcess(knp_command=knp_command,
                                        juman_command=juman_command,
                                        juman_options=juman_options,
                                        knp_options=knp_options,
                                        process_mode=process_mode,
                                        path_juman_rc=path_juman_rc,
                                        eos_pattern="EOS",
                                        is_use_jumanpp=is_use_jumanpp,
                                        timeout_second=timeout_seconds)
    parsed_result = knp_process_handler.run_command(text=text)  # type: Tuple[bool,six.text_type]

    return parsed_result