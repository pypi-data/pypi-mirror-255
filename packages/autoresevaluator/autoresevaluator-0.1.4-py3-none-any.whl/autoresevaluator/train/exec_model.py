import numpy as np
from ..utils.codefix import codefix
from ..utils.log_config import setup_logging
from .load_method import load_method_from_path
import traceback
import sys

_, model_logger = setup_logging()

def exec_model(copy_file_path, X_train, y_train, X_test, params):
    retry_limit = 10  # 最大試行回数
    retry_count = 0  # 現在の試行回数

    while retry_count < retry_limit:
        try:
            model = load_method_from_path(copy_file_path)
            y_pred = model(X_train, y_train, X_test, params)
            if not isinstance(y_pred, np.ndarray):
                raise model_logger.error("y_pred must be a NumPy array.")
            if y_pred.ndim != 1:
                raise model_logger.error("y_pred must be a one-dimensional array.")
            return y_pred
        except Exception as error:
            model_logger.error(f'Exec Error: {error}', exc_info=True)
            # モデル修正にすべてのエラー情報を渡すための処理
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
            codefix(copy_file_path, traceback_details)

            retry_count += 1  
            if retry_count >= retry_limit:
                model_logger.error("試行回数が上限に達しました")

    if retry_count < retry_limit:
        model_logger.error('処理が成功し、ループを終了しました')
    else:
        model_logger.error('最大試行回数を超えましたが、処理は成功しませんでした')


