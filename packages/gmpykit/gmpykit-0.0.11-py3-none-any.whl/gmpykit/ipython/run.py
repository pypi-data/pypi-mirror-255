from IPython import get_ipython
from IPython.core.magic import register_cell_magic

@register_cell_magic
def magic_run(line, cell):
    if eval(line):
        get_ipython().ex(cell)
    else:
        print("Cell execution skipped by run magic.")
