from argparse import Namespace
from typing import Any, List

from pydantic import StrictInt

import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.cli.registry import lookup_registry_name_by_id
from aioli.common.api import authentication
from aioli.common.api.errors import NotFoundException
from aioli.common.declarative_argparse import Arg, ArgsDescription, Cmd
from aiolirest.models.trained_model import TrainedModel
from aiolirest.models.trained_model_request import TrainedModelRequest


@authentication.required
def list_models(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.ModelsApi(session)
        response = api_instance.models_get()

    def format_model(e: TrainedModel, reg_api: aiolirest.RegistriesApi) -> List[Any]:
        rname = lookup_registry_name_by_id(e.registry, reg_api)
        result = [
            e.name,
            e.description,
            e.version,
            e.url,
            e.image,
            rname,
        ]
        return result

    headers = [
        "Name",
        "Description",
        "Version",
        "URI",
        "Image",
        "Registry",
    ]
    registries_api = aiolirest.RegistriesApi(session)
    values = [format_model(r, registries_api) for r in response]
    render.tabulate_or_csv(headers, values, args.csv)


@authentication.required
def create(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.ModelsApi(session)

        r = TrainedModelRequest(
            name=args.name,
            description=args.description,
            url=args.url,
            image=args.image,
            registry=args.registry,
        )
        api_instance.models_post(r)


def lookup_model(name: str, api: aiolirest.ModelsApi) -> TrainedModel:
    for r in api.models_get():
        if r.name == name:
            return r
    raise NotFoundException(f"model {name} not found")


def lookup_model_and_version(name: str, version: int, api: aiolirest.ModelsApi) -> TrainedModel:
    for r in api.models_get():
        if r.name == name and r.version == StrictInt(version):
            return r
    raise NotFoundException(f"model {name} version {version} not found")


@authentication.required
def update(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.ModelsApi(session)
        found = lookup_model(args.modelname, api_instance)
        request = TrainedModelRequest(
            description=found.description,
            image=found.image,
            name=found.name,
            registry=found.registry,
            url=found.url,
        )

        if args.name is not None:
            request.name = args.name

        if args.description is not None:
            request.description = args.description

        if args.url is not None:
            request.url = args.url

        if args.image is not None:
            request.image = args.image

        if args.registry is not None:
            request.registry = args.registry

        headers = {"Content-Type": "application/json"}

        assert found.id is not None
        api_instance.models_id_put(found.id, request, _headers=headers)


@authentication.required
def delete_model(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.ModelsApi(session)
        found = lookup_model_and_version(args.name, args.version, api_instance)

        assert found.id is not None
        api_instance.models_id_delete(found.id)


common_model_args: ArgsDescription = [
    Arg("--description", help="Description of the model"),
    Arg("--url", help="Reference within the specified registry"),
    Arg("--image", help="Docker container image servicing the model"),
    Arg("--registry", help="The name or ID of the model registry"),
]

main_cmd = Cmd(
    "m|odel",
    None,
    "manage trained models",
    [
        # Inspection commands.
        Cmd(
            "list ls",
            list_models,
            "list models",
            [
                Arg("--csv", action="store_true", help="print as CSV"),
            ],
            is_default=True,
        ),
        # Create command.
        Cmd(
            "create",
            create,
            "create a model",
            [
                Arg(
                    "name",
                    help="The name of the model registry. Must begin with a letter, but may "
                    "contain letters, numbers, underscore, and hyphen",
                ),
            ]
            + common_model_args,
        ),
        # Update command
        Cmd(
            "update",
            update,
            "modify a model",
            [
                Arg("modelname", help="The name of the model registry"),
                Arg(
                    "--name",
                    help="The new name of the model registry. Must begin with a letter, but may "
                    "contain letters, numbers, underscore, and hyphen",
                ),
            ]
            + common_model_args,
        ),
        Cmd(
            "delete",
            delete_model,
            "delete a model",
            [
                Arg("name", help="The name of the model registry"),
                Arg("version", help="The model version to delete"),
            ],
        ),
    ],
)

args_description = [main_cmd]  # type: List[Any]
