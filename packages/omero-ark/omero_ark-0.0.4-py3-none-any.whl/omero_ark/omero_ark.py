from pydantic import Field
from koil.composition import Composition
from .rath import OmeroArkRath


class OmeroArk(Composition):
    """The Mikro Composition

    This composition provides a datalayer and a omero_ark for interacting with the
    mikro api and beyond

    """

    rath: OmeroArkRath

    def _repr_html_inline_(self):
        return f"<table><td>rath</td><td>{self.rath._repr_html_inline_()}</td></tr></table>"
