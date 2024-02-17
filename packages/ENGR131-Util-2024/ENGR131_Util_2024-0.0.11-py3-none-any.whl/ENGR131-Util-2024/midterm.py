import drexel_jupyter_logger
from IPython import get_ipython

def engr131_midterm(execution_info):
   # Extract the cell content
   cell_content = execution_info.raw_cell
   
   # Encrypt the cell content
   encrypted_output = drexel_jupyter_logger.encrypt_output(cell_content, "7mPZKa3gJZn4ng0WJ5TsUmuQC2RK9XBAwTzrTEjbyB0=")
   
   # Replace the cell content with the encrypted output
   # Note: Depending on your requirements, you might handle this differently
   execution_info.raw_cell = encrypted_output
