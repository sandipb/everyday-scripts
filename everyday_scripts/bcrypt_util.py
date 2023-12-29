#!/usr/bin/env python3
import bcrypt
import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    pass


@click.command()
@click.argument("password")
def gen(password):
    """Generate a bcrypt hash for a given password."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    click.echo(hashed_password.decode("utf-8"))


@click.command()
@click.argument("password")
@click.argument("hash")
def match(password, hash):
    """Check if a password matches a given bcrypt hash."""

    password_bytes = password.encode("utf-8")
    hash_bytes = hash.encode("utf-8")

    if bcrypt.checkpw(password_bytes, hash_bytes):
        click.echo(click.style("The password matches the hash.", fg="green"))
    else:
        click.echo(click.style("The password does not match the hash.", fg="red"))


if __name__ == "__main__":
    cli.add_command(gen)
    cli.add_command(match)
    cli()
