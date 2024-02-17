from IPython import get_ipython
from IPython.core.magic import register_cell_magic
from ..cache import cache_creation_needed, cache_reset, set_path, cache_update_needed


@register_cell_magic
def magic_cache_it(line, cell=None):
    """Run a cell only if the given variables are not in cache. Fetch them otherwise"""

    path = "."

    if cache_creation_needed(path):
        cache_reset(path)
        print(f"[CACHE] Creation at {path}")
    else:
        set_path(path)
        print(f"[CACHE] Existing at {path}")

    cache_ready = True
    for var in line.split(" "):
        # Does a cache exists for this var?
        cache_ready = not cache_update_needed(var)
        if not cache_ready:
            break

    if not cache_ready:
        # Execute the cell
        get_ipython().ex(cell)
        # Save the result
        get_ipython().ex(f"u.cache_it('{var}', {var})")
        print("[CACHE] Cell has been executed, and result put in the cache")
    else:
        get_ipython().ex(f"{var} = u.cache_load('{var}')")
        print("[CACHE] Variables loaded from cache")
