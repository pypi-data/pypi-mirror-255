import logging
import sys

class AbstractLogger:
    _instances = {}  # Logger 인스턴스를 저장할 클래스 변수
    custom_log_level = logging.INFO  # Custom 로그 레벨을 저장할 클래스 변수

    def __new__(cls, module_name, log_level=None):
        if module_name not in cls._instances:
            # 이미 생성된 인스턴스가 없는 경우에만 새로운 인스턴스 생성
            self = super(AbstractLogger, cls).__new__(cls)
            self.logger = logging.getLogger(module_name)

            log_level = log_level or cls.custom_log_level

            if log_level:
                self.logger.setLevel(log_level)
                stdout_handler = logging.StreamHandler(sys.stdout)
                #formatter = logging.Formatter('%(asctime)s - SPARK-APP: %(name)s:%(lineno)03d - %(levelname)s - %(message)s')
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
                if log_level == logging.DEBUG:
                    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s:%(lineno)03d - %(message)s')
                stdout_handler.setFormatter(formatter)
                self.logger.addHandler(stdout_handler)

            cls._instances[module_name] = self

        return cls._instances[module_name]

    @classmethod
    def set_custom_log_level(cls, log_level):
        cls.custom_log_level = log_level

    def log(self, message, level=logging.INFO):
        self.logger.log(level, message)

    def error(self, message):
        self.log(message, level=logging.ERROR)

    def debug(self, message):
        self.log(message, level=logging.DEBUG)

    def info(self, message):
        self.log(message, level=logging.INFO)    

    def getEffectiveLevel(self):
        return self.logger.getEffectiveLevel()        
