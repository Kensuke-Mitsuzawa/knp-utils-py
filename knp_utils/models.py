#! -*- coding: utf-8 -*-
# package module
from knp_utils.logger_unit import logger
# else
from datetime import datetime
import subprocess
import traceback
import six
import re
import shutil
import pexpect
import os
import sys
from typing import List, Dict, Any, Tuple, Optional
from six import text_type
import zlib
# errors
from knp_utils.errors import ParserIntializeError


if six.PY2:
    ConnectionRefusedError = Exception
    TimeoutError = Exception


class UnixProcessHandler(object):
    """This class is a handler of any UNIX process. The class keeps UNIX process running.
    """
    def __init__(self,
                 unix_command,
                 option=None,
                 pattern='EOS',
                 timeout_second=10):
        # type: (text_type,text_type,text_type,int)->None
        self.unix_command = unix_command
        self.timeout_second = timeout_second
        self.pattern = pattern
        self.option = option
        self.launch_process(unix_command)

    def __del__(self):
        if hasattr(self, "process_analyzer"):
            self.process_analyzer.kill(sig=9)

    def launch_process(self, command):
        # type: (text_type)->None
        """* What you can do
        - It starts jumanpp process and keep it.
        """
        if not self.option is None:
            command_plus_option = self.unix_command + " " + self.option
        else:
            command_plus_option = self.unix_command

        if six.PY3:
            if shutil.which(command) is None:
                raise Exception("No command at {}".format(command))
            else:
                self.process_analyzer = pexpect.spawnu(command_plus_option)
                self.process_id = self.process_analyzer.pid
        else:
            doc_command_string = "echo '' | {}".format(command)
            command_check = os.system(doc_command_string)
            if not command_check == 0:
                raise Exception("No command at {}".format(command))
            else:
                self.process_analyzer = pexpect.spawnu(command_plus_option)
                self.process_id = self.process_analyzer.pid

    def restart_process(self):
        # type: ()->None
        """"""
        if not self.option is None:
            command_plus_option = self.unix_command + " " + self.option
        else:
            command_plus_option = self.unix_command

        self.process_analyzer.kill(sig=9)
        self.process_analyzer = pexpect.spawnu(command_plus_option)
        self.process_id = self.process_analyzer.pid

    def stop_process(self):
        # type: ()->bool
        """* What you can do
        - You're able to stop the process which this instance has now.
        """
        if hasattr(self, "process_analyzer"):
            self.process_analyzer.kill(sig=9)
        else:
            pass

        return True

    def __query(self, input_string):
        # type: (text_type)->text_type
        """* What you can do
        - It takes the result of Juman++
        - This function monitors time which takes for getting the result.
        """
        input_encoded = input_string
        self.process_analyzer.sendline(input_encoded)
        buffer = ""
        while True:
            line_string = self.process_analyzer.readline()  # type: text_type
            if line_string.strip() == input_string:
                """Skip if process returns the same input string"""
                continue
            elif line_string.strip() == self.pattern:
                buffer += line_string
                return buffer
            else:
                buffer += line_string

    def __notify_handler(self, signum, frame):
        raise Exception("""It takes longer time than {time} seconds. You're able to try, 
        1. Change your setting of 'timeout_second' parameter
        2. Run restart_process() method when the exception happens.""".format(**{"time": self.timeout_second}))

    def query(self, input_string):
        # type: (text_type)->text_type
        """* What you can do
        """
        try:
            return self.__query(input_string=input_string)
        except UnicodeDecodeError:
            logger.error(msg=traceback.format_exc())
            raise Exception()


class SubprocessHandler(object):
    """A old fashion way to keep connection into UNIX process"""
    def __init__(self, command, timeout_second=None):
        # type: (text_type,int)->None
        subproc_args = {'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE,
                        'stderr': subprocess.STDOUT, 'cwd': '.',
                        'close_fds': sys.platform != "win32"}
        try:
            env = os.environ.copy()
            self.process = subprocess.Popen('bash -c "%s"' % command, env=env,
                                            shell=True, **subproc_args)
        except OSError:
            raise ParserIntializeError(message='Failed to initialize parser.', path_to_parser=command)

        self.command = command
        (self.stdouterr, self.stdin) = (self.process.stdout, self.process.stdin)
        if timeout_second is None:
            self.timeout_second = 10000000
        else:
            self.timeout_second = timeout_second


    def __del__(self):
        self.process.stdin.close()
        self.process.stdout.close()
        try:
            self.process.kill()
            self.process.wait()
        except OSError:
            pass

    def query(self, sentence, eos_pattern, document_type):
        #  type: (text_type, text_type, text_type)->text_type
        assert (isinstance(sentence, six.text_type))
        if document_type == 'juman':
            if isinstance(sentence, six.text_type) and six.PY2:
                # python2で入力がunicodeだった場合の想定 #
                self.process.stdin.write(sentence.encode('utf-8') + '\n'.encode('utf-8'))
            elif isinstance(sentence, str) and six.PY2:
                self.process.stdin.write(sentence + '\n'.encode('utf-8'))
            elif isinstance(sentence, str) and six.PY3:
                self.process.stdin.write(sentence.encode('utf-8') + '\n'.encode('utf-8'))
        elif document_type=='knp':
            if isinstance(sentence, six.text_type) and six.PY2:
                # python2で入力がunicodeだった場合の想定 #
                self.process.stdin.write(sentence.encode('utf-8'))
            elif isinstance(sentence, str) and six.PY2:
                self.process.stdin.write(sentence)
            elif isinstance(sentence, str) and six.PY3:
                self.process.stdin.write(sentence.encode('utf-8'))

        self.process.stdin.flush()
        if six.PY2:
            result = "".encode('utf-8')
        elif six.PY3:
            result = "".encode('utf-8')
        else:
            raise Exception()

        start_time = datetime.now()
        eos_pattern_byte = eos_pattern.encode('utf-8')
        no_file_pattern_byte = r'No\ssuch\sfile\sor\sdirectory'.encode('utf-8')
        while True:
            line = self.stdouterr.readline()[:-1]
            result = result + line + "\n".encode('utf-8')
            if re.search(eos_pattern_byte, line):
                break
            if re.search(pattern=no_file_pattern_byte, string=result):
                raise ParserIntializeError(message=result, path_to_parser=self.command)

            elapsed_time = (datetime.now() - start_time).seconds
            if elapsed_time > self.timeout_second:
                raise TimeoutError("It wastes longer time than {}".format(self.timeout_second))

        result_unicode = result.decode('utf-8')
        return result_unicode


class KnpSubProcess(object):
    """This class defines process to run KNP analysis."""
    def __init__(self,
                 knp_command,
                 juman_command,
                 knp_options=None,
                 juman_options=None,
                 knp_server_host=None,
                 knp_server_port=None,
                 juman_server_host=None,
                 juman_server_port=None,
                 is_use_jumanpp=False,
                 process_mode='subprocess',
                 path_juman_rc=None,
                 eos_pattern="EOS",
                 timeout_second=60):
        # type: (str,str,str,str,str,int,str,int,bool,str,str,str,int)->None
        """* Parameters
        - knp_command: Path into Bin of KNP
        - juman_command: Path into Bin of Juman(or Juman++)
        - knp_options: Option strings of KNP(or KNP++)
        - juman_options: Option string of Juman(or Juman++)
        - knp_server_host: Host address where KNP server is working
        - knp_server_port: Port number where KNP server is working
        - juman_server_host: Host address where Juman server is working
        - juman_server_port: Port number where Juman server is working
        - is_use_jumanpp: Bool flag to use Juman++ instead of Juman. You're supposed to install Juman++ beforehand.
        - process_mode: Way to call UNIX commands. 1; You call UNIX commands everytime. 2; You keep UNIX commands running.
        - path_juman_rc: Path into Jumanrc file.
        """
        PROCESS_MODE = ('everytime', 'pexpect', 'subprocess')

        self.knp_command = knp_command
        self.juman_command = juman_command
        self.juman_options = juman_options
        self.knp_options = knp_options
        self.knp_server_host = knp_server_host
        self.knp_server_port = knp_server_port
        self.juman_server_host = juman_server_host
        self.juman_server_port = juman_server_port
        self.path_juman_rc = path_juman_rc
        self.is_use_jumanpp = is_use_jumanpp
        self.process_mode = process_mode
        self.eos_pattern = eos_pattern
        self.timeout_second = timeout_second

        # Check jumanrc file path #
        if not self.path_juman_rc is None and not os.path.exists(self.path_juman_rc):
            raise Exception("No jumanrc file at {}".format(self.path_juman_rc))
        else:
            pass

        # Check flag combination & show warning message for a user #
        if not self.path_juman_rc is None:
            if self.is_use_jumanpp:
                logger.warning("path_juman_rc is invalid when is_use_jumanpp is True.")
            elif not self.juman_server_host is None:
                logger.warning("path_juman_rc is invalid when you use juman server mode.")
            else:
                pass
        else:
            pass

        if not self.process_mode in PROCESS_MODE:
            raise Exception("No process_mode named {}".format(self.process_mode))
        else:
            pass

        if os.name=='nt' and self.process_mode=='pexpect':
            logger.warning(msg="You could not use process_mode='pexpect' in Windows. It forces set process_mode = 'everytime'")
        else:
            pass

        # choose a way to call unix commands #
        if (not self.juman_server_host is None and not self.juman_server_port is None) and (not self.knp_server_host is None and self.knp_server_port is None):
            self.__launch_server_model()
        elif self.process_mode == 'pexpect':
            self.__launch_pexpect_mode()
        elif self.process_mode == 'everytime':
            self.__launch_everytime_mode()
        elif self.process_mode == 'subprocess':
            self.__launch_subprocess_model()
        else:
            raise Exception("It failed to initialize. Check your configurations.")

    def __launch_subprocess_model(self):
        # type: ()->None
        """* What you can do
        - It defines process with subprocess handler
        """
        self.validate_arguments()
        if self.juman_options is None:
            self.juman = SubprocessHandler(command='{}'.format(self.juman_command), timeout_second=self.timeout_second)
        else:
            self.juman = SubprocessHandler(command='{} {}'.format(self.juman_command, self.juman_options), timeout_second=self.timeout_second)

        if self.knp_options is None:
            self.knp = SubprocessHandler(command='{} -tab'.format(self.knp_command), timeout_second=self.timeout_second)
        else:
            self.knp = SubprocessHandler(command='{} {}'.format(self.knp_command, self.knp_options), timeout_second=self.timeout_second)

    def __launch_pexpect_mode(self, is_keep_process=True):
        # type: (bool)->None
        """* What you can do
        - It defines process with pexpect
        - For KNP
            - with keep process running (experimental)
            - with launching KNP command every time
        """
        self.validate_arguments()
        # set juman/juman++ unix process #
        if self.is_use_jumanpp:
            self.juman = UnixProcessHandler(unix_command=self.juman_command,
                                            timeout_second=self.timeout_second,
                                            option=self.juman_options)
        else:
            if not self.path_juman_rc is None:
                option_string = ' '.join(['-r', self.path_juman_rc])
            elif not self.juman_options is None:
                option_string = self.juman_options
            else:
                option_string = None
            self.juman = UnixProcessHandler(unix_command=self.juman_command,
                                            option=option_string,
                                            timeout_second=self.timeout_second)
        # set KNP process #
        if is_keep_process:
            self.knp = SubprocessHandler(command='knp -tab')
        elif not self.knp_options is None:
            self.knp = [self.knp_command, self.knp_options]
        else:
            self.knp = [self.knp_command, '-tab']

    def __launch_everytime_mode(self):
        """"""
        self.validate_arguments()
        # set juman/juman++ unix command #
        if self.is_use_jumanpp:
            self.juman = [self.juman_command]
        else:
            if not self.path_juman_rc is None:
                self.juman = [self.juman_command, '-B', '-e2', '-r', self.path_juman_rc]
            elif not self.juman_options is None:
                self.juman = [self.juman_command] + self.juman_options.split()
            else:
                self.juman = [self.juman_command, '-B', '-e2']

        # set KNP unix command #
        if not self.knp_options is None:
            self.knp = [self.knp_command] + self.knp_options.split()
        else:
            self.knp = [self.knp_command, '-tab']

    def __launch_server_model(self):
        """"""
        self.juman = [self.juman_command, '-C', '{}:{}'.format(self.juman_server_host, self.juman_server_port)]
        self.knp = [self.knp_command, '-C', '{}:{}'.format(self.knp_server_host, self.knp_server_port), '-tab']

    def validate_arguments(self):
        # argumentの検証方法を考えること
        if six.PY3:
            if shutil.which(self.juman_command) is None:
                raise Exception("No command at {}".format(self.juman_command))
            if shutil.which(self.knp_command) is None:
                raise Exception("No command at {}".format(self.juman_command))
        elif six.PY2:
            doc_command_string = "echo '' | {}".format(self.juman_command)
            command_check = os.system(doc_command_string)
            if not command_check == 0:
                raise Exception("No command at {}".format(self.juman_command))

            doc_command_string = "echo '' | {}".format(self.knp_command)
            command_check = os.system(doc_command_string)
            if not command_check == 0:
                raise Exception("No command at {}".format(self.knp_command))

        # Check options either of under Python2.x or Python3.x
        if not self.juman_options is None:
            echo_process = ["echo", '']
            echo_ps = subprocess.Popen(echo_process, stdout=subprocess.PIPE)
            p = subprocess.Popen([self.juman_command] + self.juman_options.split(),
                                 stdin=echo_ps.stdout,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=False)
            error_lines = p.stderr.readlines()  # type: List[bytes]
            error_lines_str = [line.decode() for line in error_lines]
            for line in error_lines_str:
                if re.match('^usage:', line.lower()):
                    raise Exception("Invalid options: {} {}".format(self.juman_command, self.juman_options))

        if not self.knp_options is None:
            echo_process = ["echo", '']
            echo_ps = subprocess.Popen(echo_process, stdout=subprocess.PIPE)
            echo_ps.wait()
            if self.juman_options is None:
                juman_command = [self.juman_command]
            else:
                juman_command = [self.juman_command] + self.juman_options.split()
            juman_ps = subprocess.Popen(juman_command, stdin=echo_ps.stdout, stdout=subprocess.PIPE)
            juman_ps.wait()
            p = subprocess.Popen([self.knp_command] + self.knp_options.split(),
                                 stdin=juman_ps.stdout,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=False)
            error_lines = p.stderr.readlines()  # type: List[bytes]
            error_lines_str = [line.decode() for line in error_lines]
            for line in error_lines_str:
                if re.match('^usage:', line.lower()):
                    raise Exception("Invalid options: {} {}".format(self.knp_command, self.knp_options))

    def __run_subprocess_mode(self, input_string):
        # type: (text_type)->Tuple[bool,text_type]
        assert isinstance(self.juman, SubprocessHandler)
        assert isinstance(self.knp, SubprocessHandler)

        try:
            juman_result = self.juman.query(input_string, '^EOS', 'juman')
            knp_result = self.knp.query(juman_result, '^EOS', 'knp')
            return (True, knp_result)
        except UnicodeDecodeError:
            traceback_message = traceback.format_exc()
            logger.error("Error with command={}".format(traceback.format_exc()))
            return (False, 'error with UnicodeDecodeError traceback={}'.format(traceback_message))
        except TimeoutError:
            traceback_message = traceback.format_exc()
            logger.error("Error with command={}".format(traceback.format_exc()))
            return (False, 'error with TimeoutErro traceback={}'.format(traceback_message))
        except Exception:
            traceback_message = traceback.format_exc()
            logger.error("Error with command={}".format(traceback.format_exc()))
            return (False, 'error traceback={}'.format(traceback_message))

    def __run_pexpect_mode(self, input_string):
        # type: (text_type)->Tuple[bool,text_type]
        """* What you can do
        - It calls Juman in UNIX process.
        - It calls KNP
            - with keep process running
            - with launching KNP command everytime
        """
        assert isinstance(self.juman, UnixProcessHandler)
        try:
            juman_result = self.juman.query(input_string=input_string)
        except:
            return (False, 'error traceback={}'.format(traceback.format_exc()))

        if isinstance(self.knp, SubprocessHandler):
            try:
                parsed_result = self.knp.query(sentence=juman_result.strip(), eos_pattern='^EOS')
                return (True, parsed_result)
            except:
                traceback_message = traceback.format_exc()
                return (False, 'error traceback={}'.format(traceback_message))
        else:
            # Delete final \n of Juman result document. This \n causes error at KNP #
            echo_process = ["echo", juman_result.strip()]
            try:
                echo_ps = subprocess.Popen(echo_process, stdout=subprocess.PIPE)
                echo_ps.wait()
                parsed_result = subprocess.check_output(self.knp, stdin=echo_ps.stdout)
                if six.PY2:
                    return (True, parsed_result)
                else:
                    return (True, parsed_result.decode('utf-8'))
            except subprocess.CalledProcessError:
                traceback_message = traceback.format_exc()
                logger.error("Error with command={}".format(traceback.format_exc()))
                return (False, 'error with CalledProcessError. traceback={}'.format(traceback_message))
            except UnicodeDecodeError:
                traceback_message = traceback.format_exc()
                logger.error("Error with command={}".format(traceback.format_exc()))
                return (False, 'error with UnicodeDecodeError traceback={}'.format(traceback_message))
            except Exception:
                traceback_message = traceback.format_exc()
                logger.error("Error with command={}".format(traceback.format_exc()))
                return (False, 'error traceback={}'.format(traceback_message))

    def __run_everytime_mode(self, input_string):
        # type: (text_type)->Tuple[bool,text_type]
        assert isinstance(self.juman, list)
        assert isinstance(self.knp, list)
        echo_process = ["echo", input_string]
        try:
            echo_ps = subprocess.Popen(echo_process, stdout=subprocess.PIPE)
            echo_ps.wait()
            juman_ps = subprocess.Popen(self.juman, stdin=echo_ps.stdout, stdout=subprocess.PIPE)
            juman_ps.wait()
            parsed_result = subprocess.check_output(self.knp, stdin=juman_ps.stdout)

            if six.PY2:
                return (True, parsed_result)
            else:
                return (True, parsed_result.decode('utf-8'))
        except subprocess.CalledProcessError:
            traceback_message = traceback.format_exc()
            logger.error("Error with command={}".format(traceback.format_exc()))
            return (False, 'error with CalledProcessError. traceback={}'.format(traceback_message))
        except UnicodeDecodeError:
            traceback_message = traceback.format_exc()
            logger.error("Error with command={}".format(traceback.format_exc()))
            return (False, 'error with UnicodeDecodeError traceback={}'.format(traceback_message))
        except Exception:
            traceback_message = traceback.format_exc()
            logger.error("Error with command={}".format(traceback.format_exc()))
            return (False, 'error traceback={}'.format(traceback_message))

    def __run_server_model(self, input_string):
        # type: (text_type)->Tuple[bool,text_type]
        assert isinstance(self.juman, list)
        assert isinstance(self.knp, list)
        echo_process = ["echo", input_string]
        try:
            echo_ps = subprocess.Popen(echo_process, stdout=subprocess.PIPE)
            echo_ps.wait()
            juman_ps = subprocess.Popen(self.juman, stdin=echo_ps.stdout, stdout=subprocess.PIPE)
            juman_ps.wait()
            parsed_result = subprocess.check_output(self.knp, stdin=juman_ps.stdout)

            if six.PY2:
                return (True, parsed_result)
            else:
                return (True, parsed_result.decode('utf-8'))
        except subprocess.CalledProcessError:
            traceback_message = traceback.format_exc()
            logger.error("Error with command={}".format(traceback.format_exc()))
            return (False, 'error with CalledProcessError. traceback={}'.format(traceback_message))
        except UnicodeDecodeError:
            traceback_message = traceback.format_exc()
            logger.error("Error with command={}".format(traceback.format_exc()))
            return (False, 'error with UnicodeDecodeError traceback={}'.format(traceback_message))
        except Exception:
            traceback_message = traceback.format_exc()
            logger.error("Error with command={}".format(traceback.format_exc()))
            return (False, 'error traceback={}'.format(traceback_message))

    def run_command(self, text):
        # type: (text_type)->Tuple[bool,text_type]
        """* What you can do
        - You run analysis of Juman(Juman++) and KNP.
        - You have 2 ways to call commands. 
        """
        if (not self.juman_server_host is None and not self.juman_server_port is None) and (not self.knp_server_host is None and self.knp_server_port is None):
            return self.__run_server_model(text)
        elif self.process_mode == 'pexpect':
            return self.__run_pexpect_mode(text)
        elif self.process_mode == 'everytime':
            return self.__run_everytime_mode(text)
        elif self.process_mode == 'subprocess':
            return self.__run_subprocess_mode(text)
        else:
            raise Exception("It failed to initialize. Check your configurations.")



## For keeping old version
Params = KnpSubProcess


class DocumentObject(object):
    __slots__ = ('record_id', 'status', 'text',
                 'is_success', 'timestamp', 'updated_at',
                 'sub_id', 'sentence_index', 'parsed_result', 'document_args', 'is_compress')

    def __init__(self,
                 record_id,
                 text,
                 status,
                 parsed_result=None,
                 is_success=None,
                 sub_id=None,
                 sentence_index=None,
                 timestamp=datetime.now(),
                 updated_at=datetime.now(),
                 document_args=None):
        # type: (int,text_type,bool,Optional[text_type],bool,str,int,datetime,datetime,Dict[str, Any]) -> None
        """

        :param record_id: unique id in backend DB
        :param text: input text to be parsed.
        :param status: boolean flag to describe status of knp parsing.
        :param parsed_result: parsing result text.
        :param is_success: boolean flag to describe status of knp parsing.
        :param sub_id: id in the original given text.
         This is used when the original input text is too long and the original text is separated.
        :param sentence_index: sentence index when the original input text is separated.
        :param timestamp:
        :param updated_at:
        :param document_args: dict object which is attribute information for input document.
        """
        self.record_id = record_id
        self.status = status
        self.timestamp = timestamp
        self.updated_at = updated_at
        self.is_success = is_success
        self.sentence_index = sentence_index
        self.document_args = document_args
        if six.PY2:
            try:
                if isinstance(text, str):
                    self.text = text.decode('utf-8')
                else:
                    self.text = text
            except UnicodeDecodeError:
                logger.error(traceback.format_exc())

            try:
                if isinstance(sub_id, str):
                    self.sub_id = sub_id.decode('utf-8')
                else:
                    self.sub_id = sub_id
            except UnicodeDecodeError:
                logger.error(traceback.format_exc())

            try:
                if isinstance(parsed_result, str):
                    self.parsed_result = parsed_result.decode('utf-8')
                else:
                    self.parsed_result = parsed_result
            except UnicodeDecodeError:
                logger.error(traceback.format_exc())
        else:
            self.text = text
            self.sub_id = sub_id
            self.parsed_result = parsed_result

    def set_knp_parsed_result(self, t_parsed_result):
        # type: (Tuple[bool,text_type])->None
        """* What you can do
        - It sets KNP parsed result
        """
        if t_parsed_result[0] is False:
            # If it has something system error, tuple[0] is False #
            is_success_flag = False
        else:
            # It checks KNP result has error message or NOT #
            is_success_flag = self.__check_knp_result(parsed_result=t_parsed_result[1])

        self.is_success = is_success_flag
        self.parsed_result = t_parsed_result[1]

    @staticmethod
    def __check_knp_result(parsed_result):
        # type: (text_type)->bool
        """* What you can do
        - It checks if knp result is error or not
        """
        if parsed_result is None:
            return False
        elif 'error' in parsed_result.lower():
            return False
        else:
            return True

    def to_dict(self):
        # type: ()->Dict[str,Any]
        """* What you can do
        - You see parsed result with dict format
        """
        return {
            "record_id": self.record_id,
            "sub_id": self.sub_id,
            "status": self.status,
            "text": self.text,
            "is_success": self.is_success,
            "parsed_result": self.parsed_result,
            "timestamp": self.timestamp,
            "update_at": self.updated_at,
            "document_args": self.document_args
        }


class ResultObject(object):
    def __init__(self,
                 seq_document_obj,
                 path_working_db,
                 db_handler):
        # type: (List[DocumentObject],Optional[str],Any)->None
        self.seq_document_obj = seq_document_obj
        self.path_working_db = path_working_db
        self.db_handler = db_handler

    def to_dict(self):
        # type: ()->List[Dict[str,Any]]
        """* What you can do
        - You get parsed result with dict format
        """
        return [doc_obj.to_dict() for doc_obj in self.seq_document_obj]



