# AutoRes Evaluator

<a href="https://colab.research.google.com/github/fuyu-quant/autores-evaluator/blob/main/examples/logistic_regression.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

## Architecture

![ロゴ1](images/image.png)


## How to use
- Install
    - https://pypi.org/project/autoresevaluator/

```Python
pip install autoresevaluator

from autoresevaluator import AutoResEvaluator
```

- Setting
```python
# Hyperparameter setting
# Specify "type" and "args" for items to be searched in optuna.
params = {
    'lambda_l1': {'type': 'log_float', 'args': [1e-8, 10.0]},
    'lambda_l2': {'type': 'log_float', 'args': [1e-8, 10.0]},
    'num_leaves': {'type': 'int', 'args': [2, 256]},
    'feature_fraction': {'type': 'float', 'args': [0.4, 1.0]},
    'bagging_fraction': {'type': 'float', 'args': [0.4, 1.0]},
    'verbosity': -1
}


are = AutoResEvaluator(
    # task type
    task_type='tabledata binary classification',
    # dataset name
    dataset_name='titanic',
    # model file path
    model_path='/Users/tanakatouma/vscode/autores-evaluator/test/lightgbm_model.py',
    params=params,
    # Metrics you want to maximize/minimize
    valuation_index='pr_auc'
    )
```

- Execution
```python
are.exec()
```

## Output
- result.log
    - File to output the results

- model_error.log
    - File to write errors in model files
