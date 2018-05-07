import hashlib
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import suppress
from functools import wraps
from typing import List, Any, Union

from funcy import contextmanager
from toolz import keyfilter

logger = None


def sha1sum(filename):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


def ensure_directory(directory, force_recreate=True):
    """ Ensure directory will nuke provided path, and create a fresh directory.

    Args:
        directory (str): A nested path we want to ensure.
        force_recreate (bool): If True, it will always nuke the path and re-create it.
            Otherwise, it checks and returns if path already exists first.
    """
    if not force_recreate:
        with suppress(Exception):
            if os.path.isdir(directory):
                return

    with suppress(FileNotFoundError):
        shutil.rmtree(directory)

    os.makedirs(directory)


@contextmanager
def changewd(path, is_child=False):
    """
    This is a workaround function to make ipfs api work.
    If relative path is /foo/bar/baz, and global path is /x/foo/bar/baz,
    we change the current directory to /x/foo/bar, then we add baz to ipfs.
    After that, we change the directory back to the original (/x/).
    """
    current_dir = os.getcwd()
    parent_dir = "/".join(path.split('/')[:-1]).lstrip('/')
    if is_child:
        change_to_dir = os.path.join(current_dir, parent_dir)
    else:
        change_to_dir = os.path.join('/', parent_dir)
    os.chdir(change_to_dir)
    yield
    os.chdir(current_dir)


def cleanup(files):
    if type(files) == str:
        files = [files]
    with suppress(Exception):
        for f in files:
            if os.path.isfile(f):
                os.unlink(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)


def cleanup_after(fn):
    """ A decorator to be used on methods that finalize actions on temporary directory.
    The temporary directory is destroyed when wrapped function returns.
    """

    @wraps(fn)
    def wrapper(tmp_directory, *args, **kwargs):
        result = fn(tmp_directory, *args, **kwargs)
        cleanup([tmp_directory])
        return result

    return wrapper


def allowed_extension(filename, whitelist):
    return '.' in filename and filename.rsplit('.', 1)[-1] in whitelist


# logging
# -------
def log_exception():
    """ Log to sentry.io. Alternatively,
    fallback to stdout stacktrace dump."""
    global logger

    dsn = os.getenv('SENTRY_DSN')
    if dsn:
        import raven
        logger = raven.Client(dsn)

    if logger:
        logger.captureException()
    else:
        import traceback
        print(traceback.format_exc())


@contextmanager
def log_exceptions():
    try:
        yield
    except:
        log_exception()


# toolz
# -----
def keep(d, whitelist):
    return keyfilter(lambda k: k in whitelist, d)


def omit(d, blacklist):
    return keyfilter(lambda k: k not in blacklist, d)


# ---------------
# Multi-Threading
# ---------------
def ensure_list(parameter):
    return parameter if type(parameter) in (list, tuple, set) else [parameter]


def dependency_injection(fn_args, dep_args):
    """
    >>> dependency_injection([1, None, None], [2,3])
    [1, 2, 3]
    """
    fn_args = ensure_list(fn_args)
    dep_args = ensure_list(dep_args)[::-1]

    args = []
    for fn_arg in fn_args:
        next_arg = fn_arg if fn_arg is not None else dep_args.pop()
        args.append(next_arg)

    return args


def thread_multi(
        fn,
        fn_args: List[Any],
        dep_args: List[Union[Any, List[Any]]],
        fn_kwargs=None,
        max_workers=100,
        re_raise_errors=True):
    """ Run a function /w variable inputs concurrently.

    Args:
        fn: A pointer to the function that will be executed in parallel.
        fn_args: A list of arguments the function takes. None arguments will be
        displaced trough `dep_args`.
        dep_args: A list of lists of arguments to displace in `fn_args`.
        fn_kwargs: Keyword arguments that `fn` takes.
        max_workers: A cap of threads to run in parallel.
        re_raise_errors: Throw exceptions that happen in the worker pool.
    """
    if not fn_kwargs:
        fn_kwargs = dict()

    fn_args = ensure_list(fn_args)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = (executor.submit(fn, *dependency_injection(fn_args, args), **fn_kwargs)
                   for args in dep_args)

        for future in as_completed(futures):
            try:
                yield future.result()
            except Exception as e:
                log_exception()
                if re_raise_errors:
                    raise e
