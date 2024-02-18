from .openai_model import _openai_model
from .log_config import setup_logging

_, model_logger = setup_logging()

def codefix(copy_file_path, error):
    model_logger.info('------Codefix------')

    model_name = 'gpt-4-turbo-preview'

    with open(copy_file_path, 'r') as file:
        content = file.read()

    input = """
    * Python code
    ---
    {content}
    ---
    * Error message
    ---
    {error}
    ---
    Correct the "Python code" based on the "Error message". Output only the modified "Python code" without using the code block.
    """.format(
        content=content,
        error=error
        )

    output = _openai_model(model_name, input, seed = 3665)
    model_logger.info(f'output: {output}')

    with open(copy_file_path, 'w') as file:
        file.write(output)

    return
