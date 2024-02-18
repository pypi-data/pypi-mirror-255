import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentError, ArgumentParser
from typing import List

import argcomplete
import argcomplete.completers
from termcolor import colored
from urllib3.exceptions import MaxRetryError

import aioli
from aioli.cli.deployment import args_description as deployment_args_description
from aioli.cli.model import args_description as model_args_description
from aioli.cli.registry import args_description as registry_args_description
from aioli.cli.service import args_description as service_args_description
from aioli.cli.user import args_description as user_args_description
from aioli.cli.version import args_description as version_args_description
from aioli.cli.version import check_version
from aioli.common import api
from aioli.common.declarative_argparse import Arg, ArgsDescription, add_args
from aioli.common.util import debug_mode, get_default_controller_address
from aiolirest.rest import ApiException

from .errors import CliError, FeatureFlagDisabled

args_description: ArgsDescription = [
    Arg("-u", "--user", help="run as the given user", metavar="username", default=None),
    Arg(
        "-c",
        "--controller",
        help="controller address",
        metavar="address",
        default=get_default_controller_address(),
    ),
    Arg(
        "-v",
        "--version",
        action="version",
        help="print CLI version and exit",
        version="%(prog)s {}".format(aioli.__version__),
    ),
]
all_args_description: ArgsDescription = (
    args_description
    + registry_args_description
    + model_args_description
    + service_args_description
    + deployment_args_description
    + version_args_description
    + user_args_description
)


def make_parser() -> ArgumentParser:
    return ArgumentParser(
        description="Aioli command-line client",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )


def die(message: str, always_print_traceback: bool = False, exit_code: int = 1) -> None:
    if always_print_traceback or debug_mode():
        import traceback

        traceback.print_exc(file=sys.stderr)

    print(colored(message, "red"), file=sys.stderr, end="\n")
    exit(exit_code)


def main(
    args: List[str] = sys.argv[1:],
) -> None:
    if sys.platform == "win32":
        # Magic incantation to make a Windows 10 cmd.exe process color-related ANSI escape codes.
        os.system("")

    # we lazily import "det deploy" but in the future we'd want to lazily import everything.
    parser = make_parser()
    add_args(parser, all_args_description)

    try:
        argcomplete.autocomplete(parser)

        parsed_args = parser.parse_args(args)

        v = vars(parsed_args)
        if not v.get("func"):
            parser.print_usage()
            parser.exit(2, "{}: no subcommand specified\n".format(parser.prog))

        try:
            check_version(parsed_args)
            parsed_args.func(parsed_args)
        except KeyboardInterrupt as e:
            raise e
        except (
            api.errors.BadRequestException,
            api.errors.BadResponseException,
            MaxRetryError,
        ) as e:
            die(f"Failed to {parsed_args.func.__name__}: {e}")
        except api.errors.CorruptTokenCacheException:
            die(
                "Failed to login: Attempted to read a corrupted token cache. "
                "The store has been deleted; please try again."
            )
        except FeatureFlagDisabled as e:
            die(f"controller does not support this operation: {e}")
        except CliError as e:
            die(e.message, exit_code=e.exit_code)
        except ArgumentError as e:
            die(e.message, exit_code=2)
        except ApiException as e:
            die(f"Failed on REST API operation {e.status}: {e.reason}: {e.body}")
        except Exception:
            die(f"Failed to {parsed_args.func.__name__}", always_print_traceback=True)
    except KeyboardInterrupt:
        die("Interrupting...", exit_code=3)
