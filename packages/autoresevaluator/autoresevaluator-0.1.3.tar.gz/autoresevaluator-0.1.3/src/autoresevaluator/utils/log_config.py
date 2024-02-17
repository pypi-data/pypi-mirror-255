import time
import logging

def setup_logging():
    # ロガー1の設定
    result_logger = logging.getLogger("ResultLogger")
    result_logger.setLevel(logging.DEBUG)
    if not result_logger.handlers:
        handler1 = logging.FileHandler('result.log', mode='w')
        formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler1.setFormatter(formatter1)
        result_logger.addHandler(handler1)

    # ロガー2の設定
    model_logger = logging.getLogger("ModelErrorLogger")
    model_logger.setLevel(logging.DEBUG)
    if not model_logger.handlers:
        handler2 = logging.FileHandler('model_error.log', mode='w')
        formatter2 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler2.setFormatter(formatter2)
        model_logger.addHandler(handler2)

    return result_logger, model_logger
