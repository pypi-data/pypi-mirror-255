import sys
import click

from .auth import auth_group

import click


@click.group()
def base():
    pass

@base.command("version")
def version():
    from hectiq_console import __version__, __path__    
    click.echo(f"Version: {__version__}")
    click.echo(f"Located: {__path__}")

def main():
    cli = click.CommandCollection(
        sources=[
            auth_group,
            base
        ]
    )
    # Standalone mode is False so that the errors can be caught by the runs
    cli(standalone_mode=False)
    sys.exit()

if __name__ == "__main__":
    main()
