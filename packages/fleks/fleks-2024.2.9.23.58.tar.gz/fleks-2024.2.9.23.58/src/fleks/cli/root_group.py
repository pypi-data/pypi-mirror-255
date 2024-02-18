"""
"""

import collections
from gettext import gettext as _

import click

import fleks


class RootGroup(click.Group):
    """ """

    def __init__(self, *args, **kwargs):
        """ """
        # NB: this is needed, otherwise main help is messy
        kwargs.update(help="")
        super().__init__(*args, **kwargs)

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """"""
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None or cmd.hidden:
                continue
            commands.append((subcommand, cmd))
        if len(commands):
            # allow for 3 times the default spacing
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)
            plugin_subs = {
                getattr(v["kls"], "cli_name", v["kls"].name): v for k, v in {}.items()
            }

            toplevel = dict(core=[], plugins=collections.defaultdict(list))
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                is_plugin = subcommand in plugin_subs
                label = ""
                if is_plugin:
                    plugin_kls = plugin_subs[subcommand]["kls"]
                    if issubclass(plugin_kls, (fleks.Plugin,)):
                        tmp = plugin_kls.cli_label
                        toplevel["plugins"][tmp].append(
                            (f"{subcommand}:", f"{cmd.help}")
                        )
                else:
                    toplevel["core"].append((f"{subcommand}:", f"{cmd.help}"))
                # category.append((f"{subcommand}", f"{label}{help}"))

            if toplevel["core"]:

                def search(rows, term):
                    return [i for i, (subc, subh) in enumerate(rows) if subc == term][0]

                order = ["plan", "apply", "config", "config-raw"]
                ordering = []
                for o in order:
                    for subc, subh in toplevel["core"]:
                        if subc == o:
                            ordering.append((subc, subh))
                            toplevel["core"].remove((subc, subh))
                toplevel["core"] = ordering + toplevel["core"]
                with formatter.section(_("Core COMMANDs")):
                    formatter.write_dl(toplevel["core"])

            for label in toplevel["plugins"]:
                with formatter.section(_(f"{label.title()} COMMANDs")):
                    formatter.write_dl(toplevel["plugins"][label])

    def format_usage(self, ctx, formatter):
        """
        :param ctx: param formatter:
        :param formatter:
        """
        # terminal_width, _ = click.get_terminal_size()
        terminal_width = 30
        click.echo("-" * terminal_width)
        super().format_usage(ctx, formatter)

    def parse_args(self, ctx, args):
        default = self.default
        originals = [args.copy(), ctx.__dict__.copy()]
        copy = [x for x in args.copy() if x != "--help"]
        ctx2 = default.make_context("default", copy)
        with ctx2:
            default.invoke(ctx2)
        return super(click.Group, self).parse_args(ctx, args)
