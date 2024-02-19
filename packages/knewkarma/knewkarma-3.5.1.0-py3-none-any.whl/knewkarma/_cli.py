# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #

import argparse
import asyncio
import os
from datetime import datetime

import aiohttp
from rich.pretty import pprint

from ._meta import PROGRAM_DIRECTORY
from ._parser import create_parser, version
from ._utils import log, save_data, pathfinder
from .api import get_updates
from .base import RedditUser, RedditSub, RedditPosts


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def execute(arguments: argparse.Namespace, function_mapping: dict):
    """
    Executes command-line arguments based on user-input.

    :param arguments: Argparse namespace object  containing parsed command-line arguments.
    :type arguments: argparse.Namespace
    :param function_mapping: A dictionary mapping command-line arguments to their functions.
    :type function_mapping: dict
    """

    # -------------------------------------------------------------------- #

    async with aiohttp.ClientSession() as request_session:
        await get_updates(session=request_session)

        mode_action = function_mapping.get(arguments.mode)
        is_executed: bool = False

        for action, function in mode_action:
            if getattr(arguments, action, False):
                call_function = await function(session=request_session)

                pprint(call_function, expand_all=True)
                is_executed = True

                # -------------------------------------------------------------------- #

                if arguments.csv or arguments.json:
                    target_directory: str = os.path.join(
                        PROGRAM_DIRECTORY, f"{arguments.mode}_{action}"
                    )
                    pathfinder(
                        directories=[
                            os.path.join(target_directory, "csv"),
                            os.path.join(target_directory, "json"),
                        ]
                    )
                    save_data(
                        data=call_function,
                        save_to_dir=target_directory,
                        save_json=arguments.json,
                        save_csv=arguments.csv,
                    )

                break

                # -------------------------------------------------------------------- #

        if not is_executed:
            log.warning(
                f"knewkarma {arguments.mode}: missing one or more expected argument(s)."
            )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


def stage():
    """
    Main entrypoint for the Knew Karma command-line interface.

    Sets up the command-line interface and command-line arguments
    """

    # -------------------------------------------------------------------- #

    parser = create_parser()
    arguments: argparse = parser.parse_args()
    start_time: datetime = datetime.now()

    # -------------------------------------------------------------------- #

    limit: int = arguments.limit
    sort = arguments.sort
    timeframe = arguments.timeframe

    # -------------------------------------------------------------------- #

    user = RedditUser(
        username=arguments.username if hasattr(arguments, "username") else None,
    )
    subreddit = RedditSub(
        subreddit=arguments.subreddit if hasattr(arguments, "subreddit") else None,
    )
    posts = RedditPosts()

    # -------------------------------------------------------------------- #

    # Mapping of command-line commands to their respective functions
    function_mapping: dict = {
        "user": [
            ("profile", lambda session: user.profile(session=session)),
            (
                "posts",
                lambda session: user.posts(
                    limit=limit, sort=sort, timeframe=timeframe, session=session
                ),
            ),
            (
                "comments",
                lambda session: user.comments(
                    limit=limit, sort=sort, timeframe=timeframe, session=session
                ),
            ),
        ],
        "subreddit": [
            ("profile", lambda session: subreddit.profile(session=session)),
            (
                "posts",
                lambda session: subreddit.posts(
                    limit=limit, sort=sort, timeframe=timeframe, session=session
                ),
            ),
        ],
        "posts": [
            (
                "front_page",
                lambda session: posts.front_page(
                    limit=limit, sort=sort, timeframe=timeframe, session=session
                ),
            ),
            (
                "search",
                lambda session: posts.search(
                    query=arguments.search,
                    limit=limit,
                    sort=sort,
                    timeframe=timeframe,
                    session=session,
                ),
            ),
            (
                "listing",
                lambda session: posts.listing(
                    listings_name=arguments.listing,
                    limit=limit,
                    sort=sort,
                    timeframe=timeframe,
                    session=session,
                ),
            ),
        ],
    }

    # -------------------------------------------------------------------- #

    if arguments.mode and arguments.mode in function_mapping:
        print(
            """
┓┏┓         ┓┏┓         
┃┫ ┏┓┏┓┓┏┏  ┃┫ ┏┓┏┓┏┳┓┏┓
┛┗┛┛┗┗ ┗┻┛  ┛┗┛┗┻┛ ┛┗┗┗┻"""
        )
        try:
            start_time: datetime = datetime.now()

            log.info(
                f"[bold]Knew Karma CLI[/] {version} started at "
                f"{start_time.strftime('%a %b %d %Y, %I:%M:%S%p')}..."
            )
            asyncio.run(execute(arguments=arguments, function_mapping=function_mapping))
        except KeyboardInterrupt:
            log.warning(f"User interruption detected ([yellow]Ctrl+C[/])")
        finally:
            log.info(f"Stopped in {datetime.now() - start_time} seconds.")
    else:
        parser.print_usage()

    # -------------------------------------------------------------------- #


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
