""" Strucutre Registration

This module is autoimported by arkitekt. It registers the default structure types with the arkitekt
structure-registry so that they can be used in the arkitekt app without having to import them.

You can of course overwrite this in your app if you need to expand to a more complex query.

"""
import logging

logger = logging.getLogger(__name__)


try:
    import rekuest
    from rekuest.structures.default import (
        get_default_structure_registry,
        Scope,
        id_shrink,
    )
    from rekuest.widgets import SearchWidget
    from omero_ark.api.schema import (
        ProjectFragment,
        aget_project,
        SearchProjectsQuery,
        aget_image,
        aget_dataset,
        ImageFragment,
        SearchImagesQuery,
        DatasetFragment,
        SearchDatasetsQuery,
    )

    structure_reg = get_default_structure_registry()
    structure_reg.register_as_structure(
        ProjectFragment,
        identifier="@omero-ark/project",
        aexpand=aget_project,
        ashrink=id_shrink,
        scope=Scope.GLOBAL,
        default_widget=SearchWidget(
            query=SearchProjectsQuery.Meta.document, ward="omero-ark"
        ),
    )
    structure_reg.register_as_structure(
        ImageFragment,
        identifier="@omero-ark/image",
        aexpand=aget_image,
        ashrink=id_shrink,
        scope=Scope.GLOBAL,
        default_widget=SearchWidget(
            query=SearchImagesQuery.Meta.document, ward="omero-ark"
        ),
    )
    structure_reg.register_as_structure(
        DatasetFragment,
        identifier="@omero-ark/dataset",
        aexpand=aget_dataset,
        ashrink=id_shrink,
        scope=Scope.GLOBAL,
        default_widget=SearchWidget(
            query=SearchDatasetsQuery.Meta.document, ward="omero-ark"
        ),
    )


except ImportError:
    pass
