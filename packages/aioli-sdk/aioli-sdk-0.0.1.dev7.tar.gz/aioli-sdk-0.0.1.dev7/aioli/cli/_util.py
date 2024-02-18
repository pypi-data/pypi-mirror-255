import argparse
from typing import Optional

import aiolirest
from aioli.common import api, util
from aioli.common.api import authentication


def setup_session_no_auth(args: argparse.Namespace) -> aiolirest.ApiClient:
    host: str = args.controller
    host = prepend_protocol(host)

    configuration = aiolirest.Configuration(host=host)
    return aiolirest.ApiClient(configuration)


def setup_session(
    args: argparse.Namespace, controller: Optional[str] = None
) -> aiolirest.ApiClient:
    # Defining the host is optional and defaults to http://localhost:8080
    # See configuration.py for a list of all supported configuration parameters.
    if controller is not None:
        host = controller
    else:
        host = args.controller

    host = prepend_protocol(host)

    configuration = aiolirest.Configuration(host=host)

    token: Optional[str] = None

    if authentication.cli_auth is not None:
        token = authentication.cli_auth.get_session_token()
    if token is None:
        token = util.get_aioli_user_token_from_env()
        # Until something more permanent is available, import a token from the environment.
        if token is None:
            raise api.errors.NotFoundException("AIOLI_USER_TOKEN not defined")

    configuration.api_key["ApiKeyAuth"] = "Bearer " + token

    return aiolirest.ApiClient(configuration)


def prepend_protocol(host: str) -> str:
    # If neither http nor https is specified, supply the default of http.
    if not (host.startswith("http://") or host.startswith("https://")):
        host = f"http://{host}"
    return host
