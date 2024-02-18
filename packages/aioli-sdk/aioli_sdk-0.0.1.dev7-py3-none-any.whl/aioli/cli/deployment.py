from argparse import Namespace
from typing import Any, List

import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.common.api import authentication
from aioli.common.api.errors import NotFoundException
from aioli.common.declarative_argparse import Arg, ArgsDescription, Cmd
from aiolirest.models.deployment import Deployment, DeploymentState
from aiolirest.models.deployment_request import DeploymentRequest


@authentication.required
def show_deployment(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)

    deployment = lookup_deployment(args.name, api_instance)

    # For a more useful display, replace the service ID with its name
    services_api = aiolirest.ServicesApi(session)
    deployment.service = services_api.services_id_get(deployment.service).name

    d = deployment.to_dict()
    # Remove clusterName for now - INF-243
    d.pop("clusterName")
    print(render.format_object_as_yaml(d))


@authentication.required
def list_deployments(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)
        response = api_instance.deployments_get()

    def format_deployment(e: Deployment, reg_api: aiolirest.ServicesApi) -> List[Any]:
        service = reg_api.services_id_get(e.service)

        state = e.state
        if state is None:
            state = DeploymentState()

        secondary_state = e.secondary_state
        if secondary_state is None:
            secondary_state = DeploymentState()

        result = [
            e.name,
            service.name,
            e.namespace,
            e.status,
            state.status,
            state.traffic_percentage,
            secondary_state.status,
            secondary_state.traffic_percentage,
        ]

        return result

    headers = [
        "Name",
        "Service",
        "Namespace",
        "Status",
        "State",
        "Traffic %",
        "Secondary State",
        "Traffic %",
    ]
    services_api = aiolirest.ServicesApi(session)
    values = [format_deployment(r, services_api) for r in response]
    render.tabulate_or_csv(headers, values, args.csv)


@authentication.required
def create(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)

        r = DeploymentRequest(
            name=args.name,
            service=args.service,
            namespace=args.namespace,
        )
        api_instance.deployments_post(r)


def lookup_deployment(name: str, api: aiolirest.DeploymentsApi) -> Deployment:
    for r in api.deployments_get():
        if r.name == name:
            return r
    raise NotFoundException(f"deployment {name} not found")


@authentication.required
def update(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)
        found = lookup_deployment(args.deploymentname, api_instance)
        request = DeploymentRequest(
            name=found.name,
            namespace=found.namespace,
            security=found.security,
            service=found.service,
        )

        if args.name is not None:
            request.name = args.name

        if args.service is not None:
            request.service = args.service

        if args.namespace is not None:
            request.namespace = args.namespace

        headers = {"Content-Type": "application/json"}
        assert found.id is not None
        api_instance.deployments_id_put(found.id, request, _headers=headers)


@authentication.required
def delete_deployment(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)
        found = lookup_deployment(args.name, api_instance)
        assert found.id is not None
        api_instance.deployments_id_delete(found.id)


common_deployment_args: ArgsDescription = [
    Arg("--service", help="Service name or ID to be deployed"),
    Arg("--namespace", help="The Kubernetes namespace to be used for the deployment"),
]

main_cmd = Cmd(
    "d|eployment",
    None,
    "manage trained deployments",
    [
        # Inspection commands.
        Cmd(
            "list ls",
            list_deployments,
            "list deployments",
            [
                Arg("--csv", action="store_true", help="print as CSV"),
            ],
            is_default=True,
        ),
        # Create command.
        Cmd(
            "create",
            create,
            "create a deployment",
            [
                Arg(
                    "name",
                    help="The name of the deployment. Must begin with a letter, but may contain "
                    "letters, numbers, underscore, and hyphen",
                ),
            ]
            + common_deployment_args,
        ),
        # Create command.
        Cmd(
            "show",
            show_deployment,
            "show a deployment",
            [
                Arg(
                    "name",
                    help="The name of the deployment.",
                ),
            ],
        ),
        # Update command
        Cmd(
            "update",
            update,
            "modify a deployment",
            [
                Arg("deploymentname", help="The name of the deployment"),
                Arg(
                    "--name",
                    help="The new name of the deployment. Must begin with a letter, but may "
                    "contain letters, numbers, underscore, and hyphen",
                ),
            ]
            + common_deployment_args,
        ),
        Cmd(
            "delete",
            delete_deployment,
            "delete a deployment",
            [
                Arg("name", help="The name of the deployment"),
            ],
        ),
    ],
)

args_description = [main_cmd]  # type: List[Any]
