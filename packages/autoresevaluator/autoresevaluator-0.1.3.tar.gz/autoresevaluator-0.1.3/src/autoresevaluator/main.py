from .utils.log_config import setup_logging

from .dataset.tabledata.titanic.preprocessing import titanic_data
from .metrix.binary_classification import binary_classification, binary_classification_objective

from .train.optuna import exec_optuna
from .train.load_method import load_method_from_path
import shutil

result_logger, _ = setup_logging()


class AutoResEvaluator():
    def __init__(
            self,
            task_type,
            dataset_name,
            model_path,
            params,
            valuation_index
            ) -> None:
        self.task_type = task_type
        self.dataset_name = dataset_name
        self.model_path = model_path
        self.params = params
        self.valuation_index = valuation_index
        self.objective = binary_classification_objective(self.valuation_index)
        self._select_dataset()
        self.model = None
        pass

    def _select_dataset(self):
        if self.task_type == 'tabledata binary classification':
            if self.dataset_name == 'titanic':
                self.dataset = titanic_data()
                self.metrix = binary_classification
            pass
        elif self.task_type == 'tabledata regression':
            pass
        elif self.task_type == 'image classification':
            pass
        elif self.task_type == 'text classification':
            pass

    def _copy_file(self):
        last_slash_index = self.model_path.rfind('/')
        directory_path = self.model_path[:last_slash_index + 1]
        copy_file_path = directory_path + 'copy_file.py'
        shutil.copyfile(self.model_path, copy_file_path)

        return copy_file_path

    def exec(self):
        #os.makedirs(directory, exist_ok=True)
        result_logger.info('------AutoRes Evaluator Start------')
        result_logger.info(f'task type: {self.task_type}')
        result_logger.info(f'dataset name: {self.dataset_name}')
        result_logger.info(f'model path: {self.model_path}')
        result_logger.info(f'valuation_index: {self.valuation_index}')
        result_logger.info(f'objective: {self.objective}')
        self.copy_file_path = self._copy_file()

        #self.model = load_method_from_path(self.copy_file_path)
        exec_optuna(self.copy_file_path, self.dataset, self.metrix, self.params, self.valuation_index, self.objective)
        pass
