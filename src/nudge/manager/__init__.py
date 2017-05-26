import logging
import os

import click
import click_log

from nudge.manager import commands
from nudge.manager.context import NudgeCommandContext, EnvName, Component, Stack
from nudge.manager.util import EnumType


_logger = logging.getLogger(__name__)


@click.group()
@click.argument('resources')
@click.option('--env', '-e', default=EnvName.DEV, type=EnumType(EnvName))
@click_log.simple_verbosity_option()
@click_log.init(__name__)
@click.pass_context
def cli(ctx, resources, env):
    ctx.obj = NudgeCommandContext(
        data_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data'),
        resources_path=resources,
        env_name=env,
    )


# cloudformation


@cli.command('build-template')
@click.argument('stack', type=EnumType(Stack))
@click.pass_obj
def build_template(cmd_ctx, stack):
    commands.build_template(cmd_ctx, stack)


@cli.command('create-stack')
@click.argument('stack', type=EnumType(Stack))
@click.pass_obj
def update_stack(cmd_ctx, stack):
    commands.build_template(cmd_ctx, stack)
    commands.update_stack(cmd_ctx, stack)


@cli.command('update-stack')
@click.argument('stack', type=EnumType(Stack))
@click.pass_obj
def update_stack(cmd_ctx, stack):
    commands.build_template(cmd_ctx, stack)
    commands.update_stack(cmd_ctx, stack)


# docker


@cli.command('release-img')
@click.argument('component', type=EnumType(Component))
@click.option('--docker-machine', '-dm', default='default')
@click.pass_obj
def release_img(cmd_ctx, component, docker_machine):
    commands.release_img(cmd_ctx, component, docker_machine)


@cli.command('build-img')
@click.argument('component', type=EnumType(Component))
@click.option('--docker-machine', '-dm', default='default')
@click.option('--no-cache', is_flag=True)
@click.pass_obj
def build_img(cmd_ctx, component, docker_machine, no_cache):
    commands.build_img(cmd_ctx, component, docker_machine, no_cache=no_cache)


if __name__ == '__main__':
    cli()
