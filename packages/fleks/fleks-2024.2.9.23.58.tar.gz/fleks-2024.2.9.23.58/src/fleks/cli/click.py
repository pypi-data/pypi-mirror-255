""" fleks.cli.click
"""

import click

from fleks.util import typing

from click import HelpFormatter  # noqa
from click import (  # noqa
    Command,
    Context,
    Group,
    argument,
    command,
    echo,
    get_current_context,
    group,
    option,
    pass_context,
    version_option,
)



def flag(*args, **kwargs):
    """ """
    kwargs.update(is_flag=True, default=kwargs.get("default", False))
    return option(*args, **kwargs)


def do_filter(item, filter_kwargs):
    """ """
    return all([getattr(item, f, None) == v for f, v in filter_kwargs.items()])


def _subcommand_tree(parent, path=tuple(), tree={}, **filter_kwargs):
    """ """
    # FIXME: unroll this thing
    tree = {
        **tree,
        **{
            path + tuple([sub]): item
            for sub, item in parent.commands.items()
            if all(
                [
                    isinstance(item, (Command,)),
                    not isinstance(item, (Group,)),
                    do_filter(item, filter_kwargs),
                ]
            )
        },
    }
    for sub, item in parent.commands.items():
        if all([isinstance(item, (Group,)), do_filter(item, filter_kwargs)]):
            children = _subcommand_tree(
                item, path=path + tuple([sub]), tree=tree, **filter_kwargs
            )
            tree.update(children)
    return tree


def subcommand_tree(parent, mode="default", path=tuple(), tree={}, **filter_kwargs):
    """ """
    err = "cannot filter with None!"
    for f, val in filter_kwargs.items():
        assert val is not None, err
    tree = _subcommand_tree(parent, path=path, tree=tree, **filter_kwargs)
    if mode == "text":
        return {" ".join(k): v for k, v in tree.items()}
    return tree


def group_merge(g1: click.Group, g2: click.Group):
    """ """

    def fxn():
        pass

    fxn.__doc__ = g1.help
    tmp = g2.group(g1.name)(fxn)
    for cmd in g1.commands.values():
        tmp.add_command(cmd)


def group_copy(g1: click.Group, **kwargs: typing.OptionalAny):
    """ """
    tmp = [[k, v] for k, v in g1.__dict__.copy().items() if not k.startswith("_")]
    tmp = dict(tmp)
    tmp.update(**kwargs)
    return click.Group(**tmp)
