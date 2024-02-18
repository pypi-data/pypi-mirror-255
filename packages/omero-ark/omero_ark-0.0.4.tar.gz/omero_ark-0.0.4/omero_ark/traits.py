"""
Traits for omero_ark


Traits are mixins that are added to every graphql type that exists on the mikro schema.
We use them to add functionality to the graphql types that extend from the base type.

Every GraphQL Model on Mikro gets a identifier and shrinking methods to ensure the compatibliity
with arkitekt. This is done by adding the identifier and the shrinking methods to the graphql type.
If you want to add your own traits to the graphql type, you can do so by adding them in the graphql
.config.yaml file.

"""

from typing import Awaitable, List, TypeVar, Tuple, Protocol, Optional
import numpy as np
from pydantic import BaseModel
import xarray as xr
import pandas as pd
from rath.links.shrink import ShrinkByID
from typing import TYPE_CHECKING
from rath.scalars import ID
from typing import Any
import pyarrow.parquet as pq

if TYPE_CHECKING:
    pass


class Image(BaseModel):
    """Image Trait

    This trait is added to every graphql type that extends from the Image type.
    It adds the identifier and the shrinking methods to the graphql type.

    """

    async def adownlaod(self, filepath: str) -> Awaitable[xr.DataArray]:
        """The Data of the Representation as an xr.DataArray. Accessible from asyncio.

        Returns:
            xr.DataArray: The associated object.

        Raises:
            AssertionError: If the representation has no store attribute quries
        """
        import aiohttp
        import aiofiles

        async with aiohttp.ClientSession() as session:
            url = self.file
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open("/some/file.img", mode="wb")
                    await f.write(await resp.read())
                    await f.close()
