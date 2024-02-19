import click
from vm import start, stop, connect  # Import the commands from vm.py

@click.group()
def cli():
    pass

cli.add_command(start)
cli.add_command(stop)
cli.add_command(connect)

if __name__ == '__main__':
    cli()
