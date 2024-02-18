import sys

import click


@click.group()
def cli():
    pass


@click.command()
def hello():
    print("Hello, world!")


cli.add_command(hello)


def main():
    cli()


if __name__ == "__main__":
    sys.exit(main())
