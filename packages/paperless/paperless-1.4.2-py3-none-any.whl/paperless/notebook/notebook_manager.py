import nbformat
from loguru import logger
from papermill.iorw import papermill_io

def save_notebook(content, notebook_path):
    logger.debug("saving notebook")
    nb = nbformat.writes(content, version=4)
    papermill_io.write(nb, notebook_path)
    logger.debug("saved notebook")

def read_notebook(notebook_path):
    logger.debug("reading notebook")
    nb = nbformat.reads(papermill_io.read(notebook_path), as_version=4)
    logger.debug("read notebook")
    return nb

