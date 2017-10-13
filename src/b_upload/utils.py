import hashlib
import os
import shutil
from contextlib import suppress
from functools import wraps

from funcy.decorators import contextmanager


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
