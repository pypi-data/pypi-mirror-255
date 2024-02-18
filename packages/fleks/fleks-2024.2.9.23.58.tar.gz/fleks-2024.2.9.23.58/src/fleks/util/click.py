""" fleks.util.click """

from click.core import Context as ClickContext


def click_recursive_help(
    cmd,
    parent=None,
    out={},
    dotpath: str = None,
    module: str = None,
    path: str = None,
    # file=sys.stdout
):
    """ """
    # source: adapted from https://stackoverflow.com/questions/57810659/automatically-generate-all-help-documentation-for-click-commands
    full_name = cmd.name
    pname = getattr(cmd, "parent", None)
    pname = parent and getattr(parent, "name", "") or ""
    ctx = ClickContext(cmd, info_name=cmd.name, parent=parent)
    help_txt = cmd.get_help(ctx)
    invocation_sample = help_txt.split("\n")[0]
    for x in "Usage: [OPTIONS] COMMAND [COMMAND] [ARGS] ...".split():
        invocation_sample = invocation_sample.replace(x, "")
    out = {
        **out,
        **{
            full_name: dict(
                name=cmd.name,
                path=path,
                dotpath=dotpath,
                module=module,
                invocation_sample=invocation_sample.lstrip().rstrip(),
                help=help_txt,
            )
        },
    }
    commands = getattr(cmd, "commands", {})
    for sub in commands.values():
        out = {
            **out,
            **click_recursive_help(
                sub, parent=ctx, dotpath=dotpath, module=module, path=path
            ),
        }
    return out
