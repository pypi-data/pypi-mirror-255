from dokker import mirror,  Deployment
import os
from koil.composition import Composition
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links.graphql_ws import GraphQLWSLink
from omero_ark.omero_ark import OmeroArk
from omero_ark.rath import (
    OmeroArkRath,
    SplitLink,
    OmeroArkRathLinkComposition,
)
from graphql import OperationType

test_path = os.path.join(os.path.dirname(__file__), "deployments", "test")


def build_deployment() -> Deployment:
    setup = mirror(test_path)
    setup.add_health_check(
        url="http://localhost:7755/graphql", service="omero_ark", timeout=5, max_retries=10
    )
    return setup


async def token_loader():
    """ Returns a token as defined in the static_token setting for omero_ark"""
    return "demo"


def build_deployed_omero_ark() -> OmeroArk:

    y = OmeroArkRath(
        link=OmeroArkRathLinkComposition(
            auth=ComposedAuthLink(
                token_loader=token_loader,
                token_refresher=token_loader,
            ),
            split=SplitLink(
                left=AIOHttpLink(endpoint_url="http://localhost:7755/graphql"),
                right=GraphQLWSLink(ws_endpoint_url="ws://localhost:7755/graphql"),
                split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
            ),
        ),
    )

    omero_ark = OmeroArk(
        rath=y,
    )
    return omero_ark


class DeployedOmeroArk(Composition):
    """ A deployed omero_ark"""
    deployment: Deployment
    omero_ark: OmeroArk


def deployed() -> DeployedOmeroArk:
    """Create a deployed omero_ark

    A deployed omero_ark is a composition of a deployment and a omero_ark.
    This means a fully functioning omero instance will be spun up when
    the context manager is entered.

    To inspect the deployment, use the `deployment` attribute.
    To interact with the omero_ark, use the `omero_ark` attribute.


    Returns
    -------
    DeployedOmeroArk
        _description_
    """
    return DeployedOmeroArk(
        deployment=build_deployment(),
        omero_ark=build_deployed_omero_ark(),
    )
