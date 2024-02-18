# If this was checked out from a git tag, this version number may not match.
# Refer to the git tag for the correct version number
try:
    import importlib.metadata

    __version__ = importlib.metadata.version("geodesic-api")
except ModuleNotFoundError:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("geodesic-api").version

from typing import Optional
from geodesic.oauth import AuthManager
from geodesic.stac import Item, Feature, FeatureCollection, Asset, STACAPI, search
from geodesic.client import Client, get_client, raise_on_error
from geodesic.raster import Raster, RasterCollection


from geodesic.entanglement.dataset import (
    Dataset,
    DatasetList,
    list_datasets,
    get_dataset,
    get_datasets,
)
from geodesic.entanglement.object import (
    get_objects,
    Object,
    Connection,
    Entity,
    Event,
    Link,
    Model,
    Concept,
    Predicate,
)
from geodesic.boson.boson import BosonConfig
from geodesic.account.projects import (
    create_project,
    get_project,
    get_projects,
    set_active_project,
    get_active_project,
    Project,
)
from geodesic.account.user import myself
from geodesic.account.credentials import Credential, get_credential, get_credentials

__all__ = [
    "authenticate",
    "Item",
    "Feature",
    "FeatureCollection",
    "Asset",
    "BosonConfig",
    "Client",
    "get_client",
    "raise_on_error",
    "Raster",
    "RasterCollection",
    "Dataset",
    "DatasetList",
    "list_datasets",
    "get_dataset",
    "get_datasets",
    "get_objects",
    "Object",
    "Entity",
    "Event",
    "Observable",
    "Property",
    "Link",
    "Model",
    "Concept",
    "Predicate",
    "Connection",
    "Project",
    "Credential",
    "get_credential",
    "get_credentials",
    "create_project",
    "get_project",
    "get_projects",
    "set_active_project",
    "get_active_project",
    "myself",
    "STACAPI",
    "search",
]


def authenticate(port_override: Optional[int] = None):
    auth = AuthManager()
    if port_override is not None:
        auth.authenticate(port=port_override)
    else:
        auth.authenticate(port=8080)
