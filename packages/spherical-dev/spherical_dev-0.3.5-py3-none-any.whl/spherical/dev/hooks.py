import os
import pathlib
import shutil

import invoke
import pkg_resources


PRE_COMMIT_FILE = '.pre-commit-config.yaml'


@invoke.task
def create_git_hooks_config(ctx, force=False):
    """Internal subtask to create default pre-commit config"""
    git_dir = ctx.run('git rev-parse --path-format=absolute --git-common-dir').stdout.strip()
    git_dir = pathlib.Path(git_dir)
    pre_commit_file_path = git_dir / '..' / PRE_COMMIT_FILE
    if pre_commit_file_path.exists() and not force:
        raise invoke.Exit('config already exists', 1)
    with open(pre_commit_file_path, 'wb') as dst:
        src = pkg_resources.resource_stream(
            __package__,
            'configs/pre-commit-config.yaml',
        )
        shutil.copyfileobj(src, dst)
    exclude = git_dir / 'info' / 'exclude'
    if exclude.exists():
        exclude_text = exclude.read_text()
        if PRE_COMMIT_FILE not in exclude_text:
            exclude_text += f'{PRE_COMMIT_FILE}{os.linesep}'
            exclude.write_text(exclude_text)

    return pre_commit_file_path


@invoke.task(
    help={
        'force': 'Replace any existing git hooks with the pre-commit script.',
    },
)
def install_git_hooks(ctx, force=False):
    """Generate pre push and pre commit scripts in .git directory of project"""
    config_path = create_git_hooks_config(ctx, force=force)
    ctx.run(
        ' '.join((
            'pre-commit install',
            '--allow-missing-config',
            '--hook-type pre-commit',
            '--hook-type pre-push',
            f'--config {config_path}',
            '--overwrite' if force else '',
        )),
    )
