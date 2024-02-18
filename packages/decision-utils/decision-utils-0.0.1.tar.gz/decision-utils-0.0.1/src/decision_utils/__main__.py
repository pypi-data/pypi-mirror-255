import click

from .watch import ModifyDecisionHandler, Watcher


@click.command()
@click.option(
    "--folder",
    default="../corpus-decisions",
    required=True,
    help="Folder to watch files for changes.",
)
def watch(folder: str):
    """Update files found in the folder based on ModifyDecisionHandler config."""
    handler = ModifyDecisionHandler()
    w = Watcher(folder, handler)
    w.run()
