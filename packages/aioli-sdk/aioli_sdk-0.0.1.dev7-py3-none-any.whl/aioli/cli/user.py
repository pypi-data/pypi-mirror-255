import getpass
from argparse import Namespace
from typing import Any, List

import aiolirest
from aioli import cli
from aioli.cli import errors, render
from aioli.common.api import authentication, certs
from aioli.common.api.errors import NotFoundException
from aioli.common.declarative_argparse import Arg, Cmd
from aiolirest.api import UsersApi
from aiolirest.models.user import User
from aiolirest.models.user_patch_request import UserPatchRequest
from aiolirest.models.user_request import UserRequest


@authentication.required
def list_users(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.UsersApi(session)
        response = api_instance.users_get()

    def format_user(u: User) -> List[Any]:
        result = [u.username, u.display_name, u.admin, u.active, u.remote]
        return result

    headers = ["Username", "Display Name", "Admin", "Active", "Remote"]
    values = [format_user(u) for u in response]
    render.tabulate_or_csv(headers, values, False)


@authentication.required
def activate_user(parsed_args: Namespace) -> None:
    patch = UserPatchRequest(active=True)
    patch_user(parsed_args, parsed_args.username, patch)


@authentication.required
def deactivate_user(parsed_args: Namespace) -> None:
    patch = UserPatchRequest(active=False)
    patch_user(parsed_args, parsed_args.username, patch)


def patch_user(
    parsed_args: Namespace,
    username: str,
    patch_data: UserPatchRequest,
) -> None:
    with cli.setup_session(parsed_args) as session:
        api_instance = aiolirest.UsersApi(session)

    user = get_user_by_name(username, api_instance)

    api_instance.users_id_patch(id=user.id, user_patch_request=patch_data)


def get_user_by_name(username: str, api_instance: UsersApi) -> User:
    for u in api_instance.users_get():
        if u.username == username:
            return u
    raise NotFoundException(f"user {username} not found")


def log_in_user(parsed_args: Namespace) -> None:
    if parsed_args.username is None:
        username = input("Username: ")
    else:
        username = parsed_args.username

    message = "Password for user '{}': ".format(username)
    password = getpass.getpass(message)

    token_store = authentication.TokenStore(parsed_args.controller)
    token = authentication.do_login(parsed_args.controller, username, password, certs.cli_cert)
    token_store.set_token(username, token)
    token_store.set_active(username)


@authentication.required
def log_out_user(parsed_args: Namespace) -> None:
    if parsed_args.all:
        authentication.logout_all(parsed_args.controller, certs.cli_cert)
    else:
        # Log out of the user specified by the command line, or the active user.
        authentication.logout(parsed_args.controller, parsed_args.user, certs.cli_cert)


@authentication.required
def change_password(parsed_args: Namespace) -> None:
    if parsed_args.target_user:
        username = parsed_args.target_user
    elif parsed_args.user:
        username = parsed_args.user
    elif authentication.cli_auth is not None:
        username = authentication.cli_auth.get_session_user()

    if not username:
        # The default user should have been set by now by autologin.
        raise errors.CliError("Please log in as an admin or user to change passwords")
    password = getpass.getpass("New password for user '{}': ".format(username))
    check_password = getpass.getpass("Confirm password: ")

    if password != check_password:
        raise errors.CliError("Passwords do not match")

    patch_data = UserPatchRequest(password=password)

    patch_user(parsed_args, username, patch_data)

    # If the target user's password isn't being changed by another user, reauthenticate after
    # password change so that the user doesn't have to do so manually.
    if parsed_args.target_user is None:
        token_store = authentication.TokenStore(parsed_args.controller)
        token = authentication.do_login(parsed_args.controller, username, password, certs.cli_cert)
        token_store.set_token(username, token)
        token_store.set_active(username)


@authentication.required
def create_user(parsed_args: Namespace) -> None:
    with cli.setup_session(parsed_args) as session:
        api_instance = aiolirest.UsersApi(session)

    admin = bool(parsed_args.admin)
    display_name: str = parsed_args.display_name
    if display_name is None:
        display_name = ""

    new_user = UserRequest(
        username=parsed_args.username,
        active=True,
        admin=admin,
        displayName=display_name,
    )
    api_instance.users_post(user=new_user)


@authentication.required
def whoami(parsed_args: Namespace) -> None:
    with cli.setup_session(parsed_args) as session:
        api_instance = aiolirest.UsersApi(session)
        user = api_instance.users_me_get()

    print("You are logged in as user '{}'".format(user.username))


# fmt: off

args_description = [
    Cmd("u|ser", None, "manage users", [
        Cmd("list ls", list_users, "list users", [], is_default=True),
        Cmd("login", log_in_user, "log in user", [
            Arg("username", nargs="?", default=None, help="name of user to log in as")
        ]),
        Cmd("change-password", change_password, "change password for user", [
            Arg("target_user", nargs="?", default=None, help="name of user to change password of")
        ]),
        Cmd("logout", log_out_user, "log out user", [
            Arg(
                "--all",
                "-a",
                action="store_true",
                help="log out of all cached sessions for the current controller",
            ),
        ]),
        Cmd("activate", activate_user, "activate user", [
            Arg("username", help="name of user to activate")
        ]),
        Cmd("deactivate", deactivate_user, "deactivate user", [
            Arg("username", help="name of user to deactivate")
        ]),
        Cmd("create", create_user, "create user", [
            Arg("username", help="name of new user"),
            Arg("--admin", action="store_true", help="give new user admin rights"),
            Arg("--display-name", default=None, help="new display name for target_user"),
        ]),
        Cmd("whoami", whoami, "print the active user", []),
    ])
]  # type: List[Any]

# fmt: on
