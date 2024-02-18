import contextlib
import copy
import functools
import os
import pathlib
import shlex
import shutil
import sys
import tempfile

import invoke
from decorator import decorator


def task_apply(task, **implicit):
    def inner(ctx, **kwargs):
        kwargs = {**kwargs, **implicit}
        empty_positionals = set(task.positional) - set(k for k, v in kwargs.items() if v is not None)
        if empty_positionals:
            raise invoke.parser.ParseError(
                f"'{task.name}' did not receive required positional arguments: {empty_positionals}",
                ctx,
            )
        return task.body(ctx, **kwargs)
    wrapper = copy.copy(task)
    wrapper.body = functools.update_wrapper(inner, task.body)
    wrapper.positional = []
    return wrapper


def check_tools(*tools, early_check=False):
    checked = [False]

    def check_which():
        if checked[0]:
            return
        for name in tools:
            if not shutil.which(name):
                raise RuntimeError('Tool `{}` not found'.format(name))
        checked[0] = True

    @decorator
    def inner(func, ctx, *args, **kwargs):
        check_which()
        return func(ctx, *args, **kwargs)

    if early_check:
        check_which()

    return inner


@contextlib.contextmanager
def chdir(target):
    last_dir = os.getcwd()
    os.chdir(target)
    try:
        yield target
    finally:
        try:
            os.chdir(last_dir)
        except OSError:
            pass


@contextlib.contextmanager
def removable_tempdir(change=False):
    target = pathlib.Path(tempfile.mkdtemp())
    try:
        with (chdir(target) if change else contextlib.nullcontext()):
            yield target
    finally:
        shutil.rmtree(target)


def ask(text):
    sys.stdout.write(text)
    sys.stdout.flush()
    try:
        if sys.platform == 'win32':
            import msvcrt
            return msvcrt.getch()
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
    finally:
        sys.stdout.write(os.linesep)


def flatten_options(labels, prefix=''):
    """Converts hierarchical list of dot separated options to dict of flat one.

    This structure:
    {'aaa':'b(`f`)','ccc.rrr':{'ddd':'eee',}}
    with prefix 'traefik' will be converted to:
    {'traefik.aaa': 'b(`f`)', 'traefik.ccc.rrr.ddd': 'eee'}
    """
    def flatten(labels, prefix):
        for name, value in labels.items():
            if prefix:
                name = f'{prefix}.{name}'
            if isinstance(value, dict):
                yield from flatten(value, name)
            else:
                yield name, value
    return dict(flatten(labels, prefix))


def named_args(flag, dct):
    """This function converts dict of named args to string of options for
    use in command line (f.e. env or label docker params).

    This structure:
    {'traefik.aaa': 'b(`f`)', 'traefik.ccc.rrr.ddd': 'eee'}
    will be converted to:
    "--label traefik.aaa='b(`f`)' --label traefik.ccc.rrr.ddd=eee"
    """
    return ' '.join(f'{flag}{k}={shlex.quote(str(v))}' for k, v in dct.items())


@invoke.task(aliases=['release', 'devpi-release', 'pypi-release', 'wheel'])
def release_warning(ctx, scm_root='.', no_isolation=False):
    from warnings import warn
    warning = 'Please install spherical-dev[release] to allow release tasks'
    warn(warning, ImportWarning)
    print(warning)
