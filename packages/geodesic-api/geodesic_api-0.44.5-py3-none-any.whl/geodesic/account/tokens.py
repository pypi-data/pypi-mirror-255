from typing import List
from geodesic.bases import _APIObject
from geodesic.client import raise_on_error
from geodesic.config import get_config
from geodesic.descriptors import _IntDescr, _StringDescr
from geodesic.service import ServiceClient
from geodesic.utils import deprecated

ted_client = ServiceClient("ted", 1, "share")


class Token(_APIObject):
    """The token class represents the share tokens created when a user shares a dataset through Ted

    Args:
        **token: values corresponding to the token and the dataset it shares
    """

    token = _StringDescr(
        doc="unique 32-bit token created by Ted and used to access a shared dataset"
    )
    servicer = _StringDescr(doc="the servicer of the dataset shared by the token")
    dataset = _StringDescr(doc="the dataset shared by the token")
    project = _StringDescr(doc="the project of the dataset shared by the token")
    ttl = _IntDescr(doc="the remaining time in seconds until the token expires")

    _limit_setitem = ["token", "servicer", "dataset", "project", "ttl"]

    def __init__(self, **token):
        self.__client = ted_client
        super().__init__(self, **token)

    @property
    def url(self) -> str:
        """
        Returns the URL that can be used to access a datset shared through Ted on the current environment

        Raises:
            requests.HTTPErrror for fault

        Returns:
            the URL to access the token in question
        """
        return "{api_host}/ted/api/v1/share/{token}/".format(
            api_host=get_config().host, token=self.token
        )

    @property
    def feature_service_url(self) -> str:
        """gets a url to an GeoServices FeatureService

        Returns a URL pointing to a feature service that can be used in ArcGIS.

        DEPRECATED: use get_feature_service_url instead
        """
        if self.servicer != "geoservices":
            raise ValueError(f"token is for '{self.servicer}', must be for 'geoservices'")
        return f"{self.url}rest/services/{self.dataset}/FeatureServer"

    @property
    def image_service_url(self) -> str:
        """gets a url to an GeoServices ImageService

        Returns a URL pointing to an image service that can be used in ArcGIS.

        DEPRECATED: use get_image_service_url instead
        """
        if self.servicer != "geoservices":
            raise ValueError(f"token is for '{self.servicer}', must be for 'geoservices'")
        return f"{self.url}rest/services/{self.dataset}/ImageServer"

    @property
    def vector_tile_service_url(self) -> str:
        """gets a url to an GeoServices VectorTileService

        Returns a URL pointing to a vector tile service that can be used in ArcGIS.

        DEPRECATED: use get_vector_tile_service_url instead
        """
        if self.servicer != "geoservices":
            raise ValueError(f"token is for '{self.servicer}', must be for 'geoservices'")
        return f"{self.url}rest/services/{self.dataset}/VectorTileServer"

    def get_vector_tile_service_url(self):
        """gets a url to an GeoServices VectorTileService

        Returns a URL pointing to a vector tile service that can be used in ArcGIS.
        """
        return self.vector_tile_service_url

    def get_image_service_url(self):
        """gets a url to an GeoServices ImageService

        Returns a URL pointing to an image service that can be used in ArcGIS.
        """
        return self.image_service_url

    def get_feature_service_url(self):
        """gets a url to an GeoServices FeatureService

        Returns a URL pointing to a feature service that can be used in ArcGIS.
        """
        return self.feature_service_url

    def get_ogc_vector_tile_url(
        self,
        collection: str = None,
        tile_matrix_set_id: str = "WebMercatorQuad",
        tile_matrix_id: str = "z",
        row_name: str = "y",
        col_name: str = "x",
        format: str = "mvt",
    ) -> str:
        """gets a url to an OGC API: Tiles service

        Returns a URL pointing to a vector tile service that can be used in web mapping.
        """
        if format not in ["mvt", "pbf", "vectors.pbf"]:
            raise ValueError(
                f"format '{format}' is not supported, must be 'mvt', 'pbf', or 'vectors.pbf'"
            )
        return self._get_ogc_tile_url(
            format,
            collection,
            tile_matrix_set_id,
            tile_matrix_id,
            row_name,
            col_name,
        )

    def get_ogc_raster_tile_url(
        self,
        collection: str = None,
        tile_matrix_set_id: str = "WebMercatorQuad",
        tile_matrix_id: str = "z",
        row_name: str = "y",
        col_name: str = "x",
        format: str = "png",
        tile_path: str = "coverage/tiles",
    ) -> str:
        """gets a url to an OGC API: Tiles service

        Returns a URL pointing to a raster tile service that can be used in web mapping.
        """
        if format not in ["png", "jpg", "jpeg", "tif"]:
            raise ValueError(
                f"format '{format}' is not supported, must be 'png', 'jpg', 'jpeg', or 'tif'"
            )
        return self._get_ogc_tile_url(
            format,
            collection,
            tile_matrix_set_id,
            tile_matrix_id,
            row_name,
            col_name,
            tile_path=tile_path,
        )

    def _get_ogc_tile_url(
        self,
        format: str,
        collection: str = None,
        tile_matrix_set_id: str = "WebMercatorQuad",
        tile_matrix_id: str = "z",
        row_name: str = "y",
        col_name: str = "x",
        tile_path: str = "tiles",
    ) -> str:
        if self.servicer != "tiles":
            raise ValueError(f"token is for '{self.servicer}', must be for 'tiles'")
        if collection is None:
            collection = self.dataset

        suffix = "{" + tile_matrix_id + "}/{" + row_name + "}/{" + col_name + "}" + f".{format}"
        dataset_root = f"{self.url}collections/{collection}/{tile_path}/{tile_matrix_set_id}/"
        return f"{dataset_root}{suffix}"

    def get_feature_layer_url(self, layer_id: int = 0) -> str:
        """gets a url to an GeoServices Feature Layer

        Returns a URL pointing to a layer that can directly be used in ArcGIS.

        Args:
            layer: the layer ID to expose

        Returns:
            a URL to to layer
        """
        return f"{self.feature_service_url}/{layer_id}"

    feature_layer_url = deprecated("1.0.0", "Token.feature_layer_url")(get_feature_layer_url)

    def update_ttl(self, ttl: int):
        """
        Update the time to live of a token in redis

        Args:
            ttl: the amount of seconds before the token should expire. Valid values are either -1,
                 representing an infinite token life, or n, where 0 < n <= 2147483647.

        Raises:
            requests.HTTPErrror for fault

        Note: If successful, nothing is returned.
        """
        raise_on_error(ted_client.patch(str(self.token) + "/" + str(ttl)))
        return

    def unshare(self):
        """
        Expires an active token created by the user, revoking access from anyone using the token

        Raises:
            requests.HTTPErrror for fault

        Note: If successful, nothing is returned. Deleting a non-existent token does not raise an error.
        """
        raise_on_error(ted_client.delete(str(self.token)))
        return


def get_tokens() -> List[Token]:
    """
    Returns all active tokens created by a user

    Raises:
        requests.HTTPErrror for fault
    """
    res = raise_on_error(ted_client.get(""))
    js = res.json()
    if js == {}:
        return []
    return [Token(**token) for token in js["tokens"]]
