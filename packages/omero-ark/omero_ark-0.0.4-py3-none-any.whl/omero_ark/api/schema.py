from omero_ark.rath import OmeroArkRath
from omero_ark.funcs import execute, aexecute
from typing_extensions import Literal
from typing import Optional, Tuple, List
from enum import Enum
from pydantic import Field, BaseModel
from datetime import datetime
from rath.scalars import ID


class ProjectFragmentDatasets(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    id: str
    name: str
    description: str

    class Config:
        """A config class"""

        frozen = True


class ProjectFragment(BaseModel):
    typename: Optional[Literal["Project"]] = Field(alias="__typename", exclude=True)
    id: str
    name: str
    description: str
    datasets: Tuple[ProjectFragmentDatasets, ...]

    class Config:
        """A config class"""

        frozen = True


class DatasetFragmentImages(BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: str
    name: str
    description: str

    class Config:
        """A config class"""

        frozen = True


class DatasetFragment(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    id: str
    name: str
    description: str
    images: Tuple[DatasetFragmentImages, ...]

    class Config:
        """A config class"""

        frozen = True


class ImageFragment(BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: str
    name: str
    description: str

    class Config:
        """A config class"""

        frozen = True


class EnsureOmeroUserMutationEnsureomerouserUser(BaseModel):
    typename: Optional[Literal["User"]] = Field(alias="__typename", exclude=True)
    id: ID
    sub: str

    class Config:
        """A config class"""

        frozen = True


class EnsureOmeroUserMutationEnsureomerouser(BaseModel):
    typename: Optional[Literal["OmeroUser"]] = Field(alias="__typename", exclude=True)
    id: ID
    omero_username: str = Field(alias="omeroUsername")
    omero_password: str = Field(alias="omeroPassword")
    user: EnsureOmeroUserMutationEnsureomerouserUser

    class Config:
        """A config class"""

        frozen = True


class EnsureOmeroUserMutation(BaseModel):
    ensure_omero_user: EnsureOmeroUserMutationEnsureomerouser = Field(
        alias="ensureOmeroUser"
    )

    class Arguments(BaseModel):
        username: str
        password: str

    class Meta:
        document = "mutation EnsureOmeroUser($username: String!, $password: String!) {\n  ensureOmeroUser(input: {username: $username, password: $password}) {\n    id\n    omeroUsername\n    omeroPassword\n    user {\n      id\n      sub\n    }\n  }\n}"


class ListProjectsQueryProjectsDatasetsImages(BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    name: str
    acquisition_date: Optional[datetime] = Field(alias="acquisitionDate")

    class Config:
        """A config class"""

        frozen = True


class ListProjectsQueryProjectsDatasets(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    name: str
    description: str
    images: Tuple[ListProjectsQueryProjectsDatasetsImages, ...]

    class Config:
        """A config class"""

        frozen = True


class ListProjectsQueryProjects(BaseModel):
    typename: Optional[Literal["Project"]] = Field(alias="__typename", exclude=True)
    name: str
    description: str
    datasets: Tuple[ListProjectsQueryProjectsDatasets, ...]

    class Config:
        """A config class"""

        frozen = True


class ListProjectsQuery(BaseModel):
    projects: Tuple[ListProjectsQueryProjects, ...]

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "query ListProjects {\n  projects {\n    name\n    description\n    datasets {\n      name\n      description\n      images {\n        name\n        acquisitionDate\n      }\n    }\n  }\n}"


class GetProjectQuery(BaseModel):
    project: ProjectFragment

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Project on Project {\n  id\n  name\n  description\n  datasets {\n    id\n    name\n    description\n  }\n}\n\nquery GetProject($id: ID!) {\n  project(id: $id) {\n    ...Project\n  }\n}"


class SearchProjectsQueryOptions(BaseModel):
    typename: Optional[Literal["Project"]] = Field(alias="__typename", exclude=True)
    value: str
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchProjectsQuery(BaseModel):
    options: Tuple[SearchProjectsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchProjects($search: String, $values: [ID!]) {\n  options: projects(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class MeQueryMeOmerouser(BaseModel):
    typename: Optional[Literal["OmeroUser"]] = Field(alias="__typename", exclude=True)
    omero_password: str = Field(alias="omeroPassword")
    omero_username: str = Field(alias="omeroUsername")

    class Config:
        """A config class"""

        frozen = True


class MeQueryMe(BaseModel):
    typename: Optional[Literal["User"]] = Field(alias="__typename", exclude=True)
    omero_user: Optional[MeQueryMeOmerouser] = Field(alias="omeroUser")

    class Config:
        """A config class"""

        frozen = True


class MeQuery(BaseModel):
    me: MeQueryMe

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "query Me {\n  me {\n    omeroUser {\n      omeroPassword\n      omeroUsername\n    }\n  }\n}"


class ListDatasetsQuery(BaseModel):
    datasets: DatasetFragment

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment Dataset on Dataset {\n  id\n  name\n  description\n  images {\n    id\n    name\n    description\n  }\n}\n\nquery ListDatasets {\n  datasets {\n    ...Dataset\n  }\n}"


class GetDatasetQuery(BaseModel):
    dataset: DatasetFragment

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Dataset on Dataset {\n  id\n  name\n  description\n  images {\n    id\n    name\n    description\n  }\n}\n\nquery GetDataset($id: ID!) {\n  dataset(id: $id) {\n    ...Dataset\n  }\n}"


class SearchDatasetsQueryOptions(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    value: str
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchDatasetsQuery(BaseModel):
    options: SearchDatasetsQueryOptions

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchDatasets($search: String, $values: [ID!]) {\n  options: datasets(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class ListImagesQueryImages(BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    name: str
    description: str

    class Config:
        """A config class"""

        frozen = True


class ListImagesQuery(BaseModel):
    images: ListImagesQueryImages

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "query ListImages {\n  images {\n    name\n    description\n  }\n}"


class GetImageQuery(BaseModel):
    image: ImageFragment

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Image on Image {\n  id\n  name\n  description\n}\n\nquery GetImage($id: ID!) {\n  image(id: $id) {\n    ...Image\n  }\n}"


class SearchImagesQueryOptions(BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    value: str
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchImagesQuery(BaseModel):
    options: SearchImagesQueryOptions

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchImages($search: String, $values: [ID!]) {\n  options: images(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


async def aensure_omero_user(
    username: str, password: str, rath: Optional[OmeroArkRath] = None
) -> EnsureOmeroUserMutationEnsureomerouser:
    """EnsureOmeroUser



    Arguments:
        username (str): username
        password (str): password
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        EnsureOmeroUserMutationEnsureomerouser"""
    return (
        await aexecute(
            EnsureOmeroUserMutation,
            {"username": username, "password": password},
            rath=rath,
        )
    ).ensure_omero_user


def ensure_omero_user(
    username: str, password: str, rath: Optional[OmeroArkRath] = None
) -> EnsureOmeroUserMutationEnsureomerouser:
    """EnsureOmeroUser



    Arguments:
        username (str): username
        password (str): password
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        EnsureOmeroUserMutationEnsureomerouser"""
    return execute(
        EnsureOmeroUserMutation, {"username": username, "password": password}, rath=rath
    ).ensure_omero_user


async def alist_projects(
    rath: Optional[OmeroArkRath] = None,
) -> List[ListProjectsQueryProjects]:
    """ListProjects



    Arguments:
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        List[ListProjectsQueryProjects]"""
    return (await aexecute(ListProjectsQuery, {}, rath=rath)).projects


def list_projects(
    rath: Optional[OmeroArkRath] = None,
) -> List[ListProjectsQueryProjects]:
    """ListProjects



    Arguments:
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        List[ListProjectsQueryProjects]"""
    return execute(ListProjectsQuery, {}, rath=rath).projects


async def aget_project(id: ID, rath: Optional[OmeroArkRath] = None) -> ProjectFragment:
    """GetProject



    Arguments:
        id (ID): id
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        ProjectFragment"""
    return (await aexecute(GetProjectQuery, {"id": id}, rath=rath)).project


def get_project(id: ID, rath: Optional[OmeroArkRath] = None) -> ProjectFragment:
    """GetProject



    Arguments:
        id (ID): id
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        ProjectFragment"""
    return execute(GetProjectQuery, {"id": id}, rath=rath).project


async def asearch_projects(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[OmeroArkRath] = None,
) -> List[SearchProjectsQueryOptions]:
    """SearchProjects



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        List[SearchProjectsQueryProjects]"""
    return (
        await aexecute(
            SearchProjectsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_projects(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[OmeroArkRath] = None,
) -> List[SearchProjectsQueryOptions]:
    """SearchProjects



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        List[SearchProjectsQueryProjects]"""
    return execute(
        SearchProjectsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def ame(rath: Optional[OmeroArkRath] = None) -> MeQueryMe:
    """Me



    Arguments:
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        MeQueryMe"""
    return (await aexecute(MeQuery, {}, rath=rath)).me


def me(rath: Optional[OmeroArkRath] = None) -> MeQueryMe:
    """Me



    Arguments:
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        MeQueryMe"""
    return execute(MeQuery, {}, rath=rath).me


async def alist_datasets(rath: Optional[OmeroArkRath] = None) -> DatasetFragment:
    """ListDatasets



    Arguments:
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        DatasetFragment"""
    return (await aexecute(ListDatasetsQuery, {}, rath=rath)).datasets


def list_datasets(rath: Optional[OmeroArkRath] = None) -> DatasetFragment:
    """ListDatasets



    Arguments:
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        DatasetFragment"""
    return execute(ListDatasetsQuery, {}, rath=rath).datasets


async def aget_dataset(id: ID, rath: Optional[OmeroArkRath] = None) -> DatasetFragment:
    """GetDataset



    Arguments:
        id (ID): id
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        DatasetFragment"""
    return (await aexecute(GetDatasetQuery, {"id": id}, rath=rath)).dataset


def get_dataset(id: ID, rath: Optional[OmeroArkRath] = None) -> DatasetFragment:
    """GetDataset



    Arguments:
        id (ID): id
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        DatasetFragment"""
    return execute(GetDatasetQuery, {"id": id}, rath=rath).dataset


async def asearch_datasets(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[OmeroArkRath] = None,
) -> SearchDatasetsQueryOptions:
    """SearchDatasets



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        SearchDatasetsQueryDatasets"""
    return (
        await aexecute(
            SearchDatasetsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_datasets(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[OmeroArkRath] = None,
) -> SearchDatasetsQueryOptions:
    """SearchDatasets



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        SearchDatasetsQueryDatasets"""
    return execute(
        SearchDatasetsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_images(rath: Optional[OmeroArkRath] = None) -> ListImagesQueryImages:
    """ListImages



    Arguments:
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        ListImagesQueryImages"""
    return (await aexecute(ListImagesQuery, {}, rath=rath)).images


def list_images(rath: Optional[OmeroArkRath] = None) -> ListImagesQueryImages:
    """ListImages



    Arguments:
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        ListImagesQueryImages"""
    return execute(ListImagesQuery, {}, rath=rath).images


async def aget_image(id: ID, rath: Optional[OmeroArkRath] = None) -> ImageFragment:
    """GetImage



    Arguments:
        id (ID): id
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        ImageFragment"""
    return (await aexecute(GetImageQuery, {"id": id}, rath=rath)).image


def get_image(id: ID, rath: Optional[OmeroArkRath] = None) -> ImageFragment:
    """GetImage



    Arguments:
        id (ID): id
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        ImageFragment"""
    return execute(GetImageQuery, {"id": id}, rath=rath).image


async def asearch_images(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[OmeroArkRath] = None,
) -> SearchImagesQueryOptions:
    """SearchImages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        SearchImagesQueryImages"""
    return (
        await aexecute(
            SearchImagesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_images(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[OmeroArkRath] = None,
) -> SearchImagesQueryOptions:
    """SearchImages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (omero_ark.rath.OmeroArkRath, optional): The omero_ark rath client

    Returns:
        SearchImagesQueryImages"""
    return execute(
        SearchImagesQuery, {"search": search, "values": values}, rath=rath
    ).options
