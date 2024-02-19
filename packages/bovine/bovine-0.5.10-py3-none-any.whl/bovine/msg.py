# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import asyncio
import click

from .utils.msg import process, validate


@click.command()  # help="Send a message through your ActivityPub Actor")
@click.option(
    "--secret",
    help="Secret corresponding to a did-key deposited with your actor",
)
@click.option("--host", help="Hostname your actor is on")
@click.option(
    "--to",
    multiple=True,
    help="Recipients either as FediVerse handle or actor id",
    default=[],
)
@click.option("--public", is_flag=True, default=False)
@click.argument("message", nargs=-1)
def main(secret, host, to, public, message):
    validate(to, public)
    asyncio.run(process(secret, host, to, public, message))


if __name__ == "__main__":
    main()
