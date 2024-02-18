# © Copyright 2024 Hewlett Packard Enterprise Development LP

import argparse
import sys
from typing import Any, Dict

import termcolor
from packaging import version

import aioli
import aioli.cli
import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.common.declarative_argparse import ArgsDescription, Cmd


def get_version(parsed_args: argparse.Namespace) -> Dict[str, Any]:
    client_info = {"version": aioli.__version__}

    controller_info = {"version": ""}

    with cli.setup_session_no_auth(parsed_args) as session:
        api_instance = aiolirest.InformationApi(session)

        try:
            response = api_instance.version_get()
            controller_info["version"] = response
        except Exception:
            # Exceptions get a pass here so that the code in check_version can complete.
            pass

    return {
        "client": client_info,
        "controller": controller_info,
        "controller_address": parsed_args.controller,
    }


def check_version(parsed_args: argparse.Namespace) -> None:
    info = get_version(parsed_args)

    controller_version = info["controller"]["version"]
    client_version = info["client"]["version"]

    if not controller_version:
        print(
            termcolor.colored(
                "Controller not found at {}. "
                "Hint: Remember to set the AIOLI_CONTROLLER environment variable "
                "to the correct controller IP and port or use the '-c' flag.".format(
                    parsed_args.controller
                ),
                "yellow",
            ),
            file=sys.stderr,
        )
    elif version.Version(client_version) < version.Version(controller_version):
        print(
            termcolor.colored(
                "CLI version {} is less than controller version {}. "
                "Consider upgrading the CLI.".format(client_version, controller_version),
                "yellow",
            ),
            file=sys.stderr,
        )
    elif version.Version(client_version) > version.Version(controller_version):
        print(
            termcolor.colored(
                "Controller version {} is less than CLI version {}. "
                "Consider upgrading the controller.".format(controller_version, client_version),
                "yellow",
            ),
            file=sys.stderr,
        )


def describe_version(parsed_args: argparse.Namespace) -> None:
    info = get_version(parsed_args)
    print(render.format_object_as_yaml(info))


args_description: ArgsDescription = [
    Cmd("version", describe_version, "show version information", [])
]
