from pydantic import Field
from rath import rath
import contextvars
from rath.links.auth import AuthTokenLink
from rath.links.compose import TypedComposedLink
from rath.links.dictinglink import DictingLink
from rath.links.file import FileExtraction
from rath.links.split import SplitLink

current_omero_ark_rath = contextvars.ContextVar("current_omero_ark_rath")


class OmeroArkRathLinkComposition(TypedComposedLink):
    """OmeroArk Rath Link Composition

    This is a composition of links that are used by the OmeroArkRath. It is a subclass of
    TypedComposedLink that adds some default links to convert files and array to support
    the graphql multipart request spec."""

    fileextraction: FileExtraction = Field(default_factory=FileExtraction)
    dicting: DictingLink = Field(default_factory=DictingLink)
    auth: AuthTokenLink
    split: SplitLink


class OmeroArkRath(rath.Rath):
    """OmeroAArk Rath

    Mikro Rath is the GraphQL client for omero_ark It is a thin wrapper around Rath
    that provides some default links and a context manager to set the current
    client. (This allows you to use the `mikro_nextrath.current` function to get the
    current client, within the context of mikro app).

    This is a subclass of Rath that adds some default links to convert files and array to support
    the graphql multipart request spec."""

    link: OmeroArkRathLinkComposition

    async def __aenter__(self):
        await super().__aenter__()
        current_omero_ark_rath.set(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        current_omero_ark_rath.set(None)
