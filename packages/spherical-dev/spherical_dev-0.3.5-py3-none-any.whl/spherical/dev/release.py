import pathlib
import sys

import invoke
from setuptools_scm import version_from_scm

from .utils import check_tools


def build(ctx, scm_root, no_isolation):
    if not version_from_scm(scm_root).exact:
        raise RuntimeError('dirty versions is not for release')
    ctx.run(
        f'python -m build --wheel{" --no-isolation" if no_isolation else ""}',
        pty=True if sys.platform != 'win32' else False,
    )
    packages = list(pathlib.Path('dist').glob('*'))
    if len(packages) != 1:
        raise RuntimeError('please cleanup (especially dist) before release')
    return packages


@invoke.task(aliases=['release'])
@check_tools('devpi', 'true')
def devpi_release(ctx, scm_root='.', no_isolation=False):
    ctx.run(
        f'devpi upload {build(ctx, scm_root, no_isolation)[0]}',
        pty=True if sys.platform != 'win32' else False,
    )


@invoke.task(aliases=['release'])
@check_tools('twine')
def pypi_release(ctx, scm_root='.', no_isolation=False):
    ctx.run(
        f'twine upload {build(ctx, scm_root, no_isolation)[0]}',
        pty=True if sys.platform != 'win32' else False,
    )


@invoke.task
def wheel(ctx, scm_root='.', no_isolation=False):
    build(ctx, scm_root, no_isolation)
