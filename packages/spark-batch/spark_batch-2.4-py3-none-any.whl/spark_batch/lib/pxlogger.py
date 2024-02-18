from spark_common.abstract_logger import AbstractLogger
import logging
import sys


# Using the same class name to achieve consistency
class CustomLogger(AbstractLogger):
    pass

#class CustomLogger:
#    _instances = {}  # Logger 인스턴스를 저장할 클래스 변수
#    custom_log_level = logging.INFO  # Custom 로그 레벨을 저장할 클래스 변수
#
#    def __new__(cls, module_name, log_level=None):
#        if module_name not in cls._instances:
#            # 이미 생성된 인스턴스가 없는 경우에만 새로운 인스턴스 생성
#            self = super(CustomLogger, cls).__new__(cls)
#            self.logger = logging.getLogger(module_name)
#            
#            log_level = log_level or cls.custom_log_level
#            
#            if log_level:
#                self.logger.setLevel(log_level)
#                stdout_handler = logging.StreamHandler(sys.stdout)
#                #formatter = logging.Formatter('%(asctime)s - SPARK-APP: %(name)s:%(lineno)03d - %(levelname)s - %(message)s')
#                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
#                if log_level == logging.DEBUG: 
#                    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s:%(lineno)03d - %(message)s')
#                stdout_handler.setFormatter(formatter)
#                self.logger.addHandler(stdout_handler)
#            
#            cls._instances[module_name] = self
#        
#        return cls._instances[module_name]
#
#    @classmethod
#    def set_custom_log_level(cls, log_level):
#        cls.custom_log_level = log_level
#        
##     def __init__(self, module_name, log_level=logging.INFO):
##         self.logger = logging.getLogger(module_name)
##         self.logger.setLevel(log_level)
#
##         # stdout 핸들러를 추가하여 로그를 표준 출력으로 출력합니다.
##         stdout_handler = logging.StreamHandler(sys.stdout)
##         formatter = logging.Formatter('%(asctime)s - SPARK-APP: %(name)s - %(levelname)s - %(message)s')
##         stdout_handler.setFormatter(formatter)
##         self.logger.addHandler(stdout_handler)
#
#    def __getattr__(self, attr):
#        # 동적으로 로그 레벨 메서드 생성
#        if hasattr(self.logger, attr):
#            log_method = getattr(self.logger, attr)
#            if callable(log_method):
#                return log_method
#        raise AttributeError(f"'CustomLogger' object has no attribute '{attr}'")
