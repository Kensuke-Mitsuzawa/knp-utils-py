#! -*- coding: utf-8 -*-
import subprocess
import traceback
import six
import socket
import re
from typing import List, Dict, Any
from knp_utils.logger_unit import logger
from knp_utils.db_handler import DocumentObject

if six.PY2:
    ConnectionRefusedError = Exception


class JumanppClient(object):
    """Class for receiving data as client"""
    def __init__(self, hostname, port, timeout=50, option=None):
        """"""
        # type:(str,int,int,None)->None
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((hostname, port))
        except ConnectionRefusedError:
            raise Exception("There is no jumanpp server hostname={}, port={}".format(hostname, port))
        except:
            raise
        if option is not None:
            self.sock.send(option)
        data = b""
        self.sock.settimeout(timeout)

    def __del__(self):
        if self.sock:
            self.sock.close()

    def query(self, sentence, pattern):
        # type: (, str, bytes) -> str
        assert (isinstance(sentence, six.text_type))
        self.sock.sendall(b"%s\n" % sentence.encode('utf-8').strip())
        data = self.sock.recv(1024)
        assert isinstance(data, bytes)
        recv = data
        while not re.search(pattern, recv):
            data = self.sock.recv(1024)
            recv = b"%s%s" % (recv, data)
        return recv.strip().decode('utf-8')


class Params(object):
    def __init__(self,
                 knp_command,
                 juman_command,
                 n_jobs=8,
                 knp_server_host=None,
                 knp_server_port=None,
                 juman_server_host=None,
                 juman_server_port=None,
                 is_use_jumanpp=None,
                 path_juman_rc=None):
        """* What you can do"""
        # type: (str,str,int,str,int,str,int,bool,str)->None
        self.n_jobs = n_jobs
        self.knp_command = knp_command
        self.juman_command = juman_command
        self.knp_server_host = knp_server_host
        self.knp_server_port = knp_server_port
        self.juman_server_host = juman_server_host
        self.juman_server_port = juman_server_port
        self.path_juman_rc = path_juman_rc
        self.is_use_jumanpp = is_use_jumanpp

    def validate_arguments(self):
        # argumentの検証方法を考えること
        try:
            subprocess.check_call(self.juman_command)
        except:
            raise Exception(traceback.format_exc())

        try:
            subprocess.check_call(self.knp_command)
        except:
            raise Exception(traceback.format_exc())

    def run_jumanpp_server(self, text):
        """"""
        # type: (str)->str
        client_obj = JumanppClient(hostname=self.juman_server_host, port=self.juman_server_port)
        parsed_result = client_obj.query(text, pattern=r'EOS')
        if self.knp_server_host is None or self.knp_server_port is None:
            knp_run_command = [self.knp_command, '-tab']
        else:
            knp_run_command = [self.knp_command, '-C', '{}:{}'.format(self.knp_server_host, self.knp_server_port), '-tab']

        parsed_result = subprocess.check_output(knp_run_command, stdin=parsed_result)
        if six.PY2:
            return parsed_result
        else:
            return parsed_result.decode('utf-8')

    def run_command(self, text):
        """* What you can do"""
        # type: (str)->str
        if self.is_use_jumanpp:
            if self.juman_server_host is None or self.juman_server_port is None:
                juman_run_command = [self.juman_command]
            else:
                return self.run_jumanpp_server(text)
        else:
            if self.juman_server_host is None or self.juman_server_port is None:
                if not self.path_juman_rc is None:
                    juman_run_command = [self.juman_command, '-r', self.path_juman_rc]
                else:
                    juman_run_command = [self.juman_command]
            else:
                juman_run_command = [self.juman_command, '-C', '{}:{}'.format(self.juman_server_host, self.juman_server_port)]

        if self.knp_server_host is None or self.knp_server_port is None:
            knp_run_command = [self.knp_command, '-tab']
        else:
            knp_run_command = [self.knp_command, '-C', '{}:{}'.format(self.knp_server_host, self.knp_server_port), '-tab']

        echo_process = ["echo", text]
        try:
            echo_ps = subprocess.Popen(echo_process, stdout=subprocess.PIPE)
            echo_ps.wait()
            juman_ps = subprocess.Popen(juman_run_command, stdin=echo_ps.stdout, stdout=subprocess.PIPE)
            juman_ps.wait()
            parsed_result = subprocess.check_output(knp_run_command, stdin=juman_ps.stdout)
            if six.PY2:
                return parsed_result
            else:
                return parsed_result.decode('utf-8')

        except subprocess.CalledProcessError:
            logger.error("Error with command={}".format(traceback.format_exc()))
            return None


class ResultObject(object):
    def __init__(self,
                 seq_document_obj,
                 path_working_db):
        """"""
        # type: (List[DocumentObject],str)->None
        self.seq_document_obj = seq_document_obj
        self.path_working_db = path_working_db

    def to_dict(self):
        """* What you can do
        - You get parsed result with dict format
        """
        # type: ()->List[Dict[str,Any]]
        return [doc_obj.to_dict() for doc_obj in self.seq_document_obj]



