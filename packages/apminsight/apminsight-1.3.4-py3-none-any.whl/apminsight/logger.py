
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from apminsight.constants import agent_logger_name, \
    logs_dir, base_dir, log_name, log_format, apm_logs_dir, PROCESS_ID, LOG_FILE_BACKUP_COUNT, LOG_FILE_SIZE, APM_LOG_FILE_BACKUP_COUNT, APM_LOG_FILE_SIZE, LOG_FILE_MODE, LOG_FILE_DELAY, LOG_FILE_ENCODEING, DEFAULT_LOG_FILE_BACKUP_COUNT, DEFAULT_LOG_FILE_SIZE

def is_non_empty_string(string):
    if not isinstance(string, str) or string == '':
        return False
    return True
class ApmLogger():
    
    __instance = None
      
    def __new__(cls, log_config):
        if cls.__instance is None:
            cls._logs_path = cls.check_and_create_dirs()
            cls.__log_file_config = [
                                      os.path.join(cls._logs_path,log_name), 
                                      LOG_FILE_MODE, 
                                      os.getenv(APM_LOG_FILE_SIZE, log_config.get(LOG_FILE_SIZE, DEFAULT_LOG_FILE_SIZE)),
                                      os.getenv(APM_LOG_FILE_BACKUP_COUNT, log_config.get(LOG_FILE_BACKUP_COUNT, DEFAULT_LOG_FILE_BACKUP_COUNT)),
                                      LOG_FILE_ENCODEING,
                                      LOG_FILE_DELAY
                                    ]
            cls.__logger = cls.create_logger()
        
        return cls.__instance
     
    @classmethod
    def check_and_create_dirs(cls):
        cus_logs_dir = os.getenv(apm_logs_dir, None)
        if not is_non_empty_string(cus_logs_dir):
            cus_logs_dir = os.getcwd()
        base_path = os.path.join(cus_logs_dir, base_dir)
        logs_path = os.path.join(base_path, logs_dir)
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
            
        return logs_path
    
    @classmethod
    def create_logger(cls):
        try:
            logger = logging.getLogger(agent_logger_name)
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter(log_format)
            cls.handler = RotatingFileHandler(*cls.__log_file_config)
            cls.handler.setFormatter(formatter)
            logger.addHandler(cls.handler)
            extra_field = {PROCESS_ID : os.getpid()}
            logger = logging.LoggerAdapter(logger, extra_field)
            return logger
        except Exception as e:
            print('apminsight agent log file initialization error', e)
            cls.log_to_sysout()

    @classmethod
    def log_to_sysout(cls):
        global agentlogger
        try:
            cls.handler = logging.StreamHandler(sys.stdout)
            agentlogger = cls.create_logger(cls.handler)
        except Exception as e:
            print('not able to print apminsight agent logs to sysout', e)
      
     
    @classmethod
    def get_logger(cls, log_config):
        if cls.__instance is None:
            cls(log_config)
        return cls.__logger 
    
    def set_log_level(level):  
        logger = ApmLogger.get_logger()
        logger.setLevel(level)

agentlogger = None    

def create_agentlogger(log_config):
    global agentlogger
    agentlogger = ApmLogger.get_logger(log_config)
    return agentlogger
