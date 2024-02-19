# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import asyncio
import json
import click

from asyncstdlib.itertools import islice
from ptpython.repl import embed

from bovine import BovineClient
from bovine.activitystreams.utils.print import print_activity


def config(repl):
    repl.use_code_colorscheme("dracula")
    repl.enable_output_formatting = True


async def repl(client):
    async with client:
        activity_factory, object_factory = client.factories
        print("The variable client contains your BovineClient")
        print("The variables activity_factory and object_factory")
        print("contain the corresponding objects")
        print("With await client.inbox() and await client.outbox()")
        print("one can interface with these two")
        print()
        await embed(
            globals=globals(),
            locals=locals(),
            return_asyncio_coroutine=True,
            patch_stdout=True,
            configure=config,
        )


async def show_inbox(client: BovineClient, max_number: int = 10, summary: bool = False):
    async with client:
        await display_box(await client.inbox(), max_number, summary)


async def show_outbox(
    client: BovineClient, max_number: int = 10, summary: bool = False
):
    async with client:
        await display_box(await client.outbox(), max_number, summary)


async def display_box(box, max_number: int, summary: bool):
    async for item in islice(box, max_number):
        if summary:
            print_activity(item)
        else:
            print(json.dumps(item, indent=2))
            print()


@click.command(help="Opens a REPL with preloaded BovineClient client")
@click.option("--domain", help="Domain the actor can be found on")
@click.option("--secret", help="Secret associated with the account")
@click.option("--config_file", help="Toml fail containing domain and secret")
@click.option("--inbox", is_flag=True, default=False, help="Display the inbox")
@click.option("--outbox", is_flag=True, default=False, help="Display the outbox")
@click.option(
    "--summary",
    is_flag=True,
    default=False,
    help="Display a summary of the activity instead of the full json",
)
@click.option(
    "--max_number",
    type=int,
    help="Number of elements to display in inbox or outbox",
    default=20,
)
def main(domain, secret, config_file, inbox, outbox, summary, max_number):
    if config_file:
        client = BovineClient.from_file(config_file)
    elif domain and secret:
        client = BovineClient(domain=domain, secret=secret)
    else:
        default_config_file = "bovine_user.toml"
        client = BovineClient.from_file(default_config_file)

        print(f"Config file not specified using fallback value '{default_config_file}'")

    if inbox:
        asyncio.run(show_inbox(client, max_number=max_number, summary=summary))
    elif outbox:
        asyncio.run(show_outbox(client, max_number=max_number, summary=summary))
    else:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(repl(client))


if __name__ == "__main__":
    main()
