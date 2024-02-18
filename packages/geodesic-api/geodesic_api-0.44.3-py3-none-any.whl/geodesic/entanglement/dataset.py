from typing import Any, Optional, Union, List, Tuple
import re
import warnings
import datetime as pydatetime
import requests

from geodesic.account.projects import Project, get_project
from geodesic.account.tokens import Token
from geodesic.bases import _APIObject
from dateutil.parser import isoparse

from geodesic.service import ServiceClient
from dateutil.parser import parse

from geodesic.descriptors import (
    _BaseDescr,
    _DictDescr,
    _ListDescr,
    _IntDescr,
    _StringDescr,
    _TimeDeltaDescr,
    _TypeConstrainedDescr,
)
from geodesic.client import get_client, raise_on_error
from geodesic.account import get_active_project
from geodesic.entanglement import Object
from geodesic.boson import (
    AssetBands,
    BosonDescr,
    BosonConfig,
    MiddlewareConfig,
    CacheConfig,
    TileOptions,
    DEFAULT_CREDENTIAL_KEY,
    STORAGE_CREDENTIAL_KEY,
)
from geodesic.stac import _AssetsDescr, Asset, STACAPI, _parse_date, Extent, Collection
from geodesic.cql import CQLFilter
import numpy as np
from geodesic.utils import DeferredImport, datetime_to_utc, deprecated
from shapely.geometry import box, MultiPolygon, shape

display = DeferredImport("IPython.display")
pyproj = DeferredImport("pyproj")
ee = DeferredImport("ee")
Image = DeferredImport("PIL", "Image")
geodesic_widgets = DeferredImport("geodesic.widgets")
arcgis = DeferredImport("arcgis")

datasets_client = ServiceClient("entanglement", 1, "datasets")
stac_client = ServiceClient("spacetime", 1, "stac")
boson_client = ServiceClient("boson", 1, "proxy")
ted_client = ServiceClient("ted", 1, "share")

stac_root_re = re.compile(r"(.*)\/collections\/")

_valid_resampling = [
    "nearest",
    "bilinear",
    "cubic",
    "cubicspline",
    "lanczos",
    "average",
    "mode",
    "max",
    "min",
    "median",
    "q1",
    "q3",
    "sum",
]


def get_dataset(
    name: str,
    project: str = None,
    version_datetime: Union[str, pydatetime.datetime] = None,
) -> "Dataset":
    """gets a Dataset from Entanglement by name

    Args:
        ids: an optional list of dataset IDs to return
        search: a search string to use to search for datasets who's name/description match
        project: the name of the project to search datasets. Defaults to the active project
        version_datetime: the point in time to search the graph - will return older versions of \
            datasets given a version_datetime.

    Returns:
        a DatasetList of matching Datasets.

    """
    dataset_list = get_datasets(ids=[name], project=project, version_datetime=version_datetime)
    if len(dataset_list) == 0:
        raise ValueError(f"dataset '{name}' not found")
    elif len(dataset_list) > 1:
        raise ValueError(
            f"more than one dataset matching '{name}' found, this should not happen, please report this"
        )

    return dataset_list[0]


def get_datasets(
    ids: Union[List, str] = [],
    search: str = None,
    project=None,
    version_datetime: Union[str, pydatetime.datetime] = None,
) -> "DatasetList":
    """searchs/returns a list of Datasets from Entanglement based on the user's query

    Args:
        ids: an optional list of dataset IDs to return
        search: a search string to use to search for datasets who's name/description match
        project: the name of the project to search datasets. Defaults to the active project
        version_datetime: the point in time to search the graph - will return older versions of \
            datasets given a version_datetime.

    Returns:
        a DatasetList of matching Datasets.

    """

    if project is None:
        project = get_active_project()
    else:
        if isinstance(project, str):
            project = get_project(project)
        elif not isinstance(project, Project):
            raise ValueError("project must be a string or Project")

    params = {}
    if ids:
        if isinstance(ids, str):
            ids = ids.split(",")
        params["ids"] = ",".join(ids)

    if search is not None:
        params["search"] = search

    params["project"] = project.uid
    # Find object versions that were valid at a specific datetime
    if version_datetime is not None:
        # check for valid format
        if isinstance(version_datetime, str):
            params["datetime"] = datetime_to_utc(isoparse(version_datetime)).isoformat()
        elif isinstance(version_datetime, pydatetime.datetime):
            params["datetime"] = datetime_to_utc(version_datetime).isoformat()
        else:
            raise ValueError(
                "version_datetime must either be RCF3339 formatted string, or datetime.datetime"
            )

    resp = datasets_client.get("", **params)
    raise_on_error(resp)

    js = resp.json()
    if js["datasets"] is None:
        return DatasetList([])

    ds = [Dataset(**r) for r in js["datasets"]]
    datasets = DatasetList(ds, ids=ids)
    return datasets


list_datasets = deprecated("1.0.0", "list_datasets")(get_datasets)


def new_union_dataset(
    name: str,
    datasets: List["Dataset"],
    feature_limit: int = 1000,
    project: Optional[Union[Project, str]] = None,
    ignore_duplicate_fields: bool = False,
    middleware: MiddlewareConfig = {},
    cache: CacheConfig = {},
    tile_options: TileOptions = {},
    domain: str = "*",
    category: str = "*",
    type: str = "*",
    **kwargs: dict,
) -> "Dataset":
    """creates a new ``union`` of ``Datasets`` that provides data from all input Datasets

    Creates a new ``Dataset`` by combining multiple ``Datasets`` with the ``union`` operation. This means
    that a query to this provider will return the combination of results from all input ``Datasets``. This
    can be filtered down by the way of the ``collections`` parameter on ``query`` and the ``asset_bands`` parameter
    in the case of a ``get_pixels`` request. All image datasets must have either all the same assets/bands or all
    different.

    Args:
        name: the name of the new ``Dataset``
        datasets: a list of ``Datasets`` to ``union``
        feature_limit: the max size of a results page from a query/search
        project: the name of the project this will be assigned to
        ignore_duplicate_fields: if True, duplicate fields across providers will be ignored
        middleware: configure any boson middleware to be applied to the new dataset.
        cache: configure caching for this dataset
        tile_options: configure tile options for this dataset

    """
    collection = _stac_collection_from_kwargs(name, **kwargs)
    _remove_keys(collection, "id", "summaries", "stac_version")

    data_api = None
    item_type = None
    for dataset in datasets:
        if data_api is None:
            data_api = dataset.data_api
            item_type = dataset.item_type
        else:
            if dataset.data_api == "stac":
                data_api = "stac"
            if item_type not in ("features", "other"):
                item_type = item_type

    properties = dict(
        providers=[
            dict(
                dataset_name=dataset.name,
                project=dataset.project.uid,
                provider_config=dataset.boson_config,
            )
            for dataset in datasets
        ],
        ignore_duplicate_fields=ignore_duplicate_fields,
    )

    boson_cfg = BosonConfig(
        provider_name="union",
        max_page_size=feature_limit,
        properties=properties,
        middleware=middleware,
        cache=cache,
        tile_options=tile_options,
    )

    return boson_dataset(
        name=name,
        alias=collection.pop("title"),
        data_api=data_api,
        item_type=item_type,
        boson_cfg=boson_cfg,
        domain=domain,
        category=category,
        type=type,
        project=project,
        **collection,
    )


class DatasetInfo(_APIObject):
    """metadata about a boson dataset.

    This is obtained by calling the dataset-info endpoint in Boson. While there is some
    field overlap, this is usually dynamically generated by Boson and is not necessarily
    the same as the metadata set by the user. Especially in cases where a creator of a
    Dataset opted to not provide much metadata, Boson attempts to generate update to date
    information, depending on the provider used.

    This is particularly useful to inspect things like valid raster assets, min/max zoom,
    available fields for querying, and STAC collections.

    """

    name = _StringDescr(doc="name of this Dataset")
    alias = _StringDescr(doc="alias - human readable name of this Dataset")
    description = _StringDescr(doc="description of this Dataset")
    overall_extent = _TypeConstrainedDescr(
        (Extent, dict), doc="spatiotemporal extent of this Dataset"
    )
    min_zoom = _IntDescr(doc="Min Zoom (OSM Zoom Value) for this layer")
    max_zoom = _IntDescr(doc="Max Zoom (OSM Zoom Value) for this layer")
    raster_assets = _DictDescr(doc="dictionary of raster-assets fro this Dataset")
    default_asset_bands = _ListDescr(
        item_type=(AssetBands, dict),
        coerce_items=True,
        doc="default asset bands that will be used for requests that render raster data",
    )
    conforms_to = _ListDescr(doc="list of OGC/other standard conformances this dataset supports")
    queryables = _DictDescr(doc="dictionary of fields that this dataset has")
    links = _ListDescr(doc="list of links for this Dataset")
    collections = _ListDescr(
        item_type=(Collection, dict),
        coerce_items=True,
        doc="list of STAC/Features Collections this Dataset has",
    )
    provider_config = _TypeConstrainedDescr((BosonConfig, dict), doc="Boson provider config")


class Dataset(Object):
    """Allows interaction with SeerAI datasets.

    Dataset provides a way to interact with datasets in the SeerAI.

    Args:
        \\*\\*obj (dict): Dictionary with all properties in the dataset.

    Attributes:
        alias(str): Alternative name for the dataset. This name has fewer restrictions on characters and should be human
        readable.

    """

    item = _DictDescr(doc="the contents of the dataset definition")
    alias = _StringDescr(nested="item", doc="the alias of this object, anything you wish it to be")
    data_api = _StringDescr(nested="item", doc="the api to access the data")
    item_type = _StringDescr(nested="item", doc="the api to access the data")
    item_assets = _AssetsDescr(
        nested="item", doc="information about assets contained in this dataset"
    )
    extent = _TypeConstrainedDescr(
        (Extent, dict), nested="item", doc="spatiotemporal extent of this Dataset"
    )
    services = _ListDescr(
        nested="item",
        item_type=str,
        doc="list of services that expose the data for this dataset",
    )
    providers = _ListDescr(nested="item", doc="list of providers for this dataset")
    stac_extensions = _ListDescr(nested="item", doc="list of STAC extensions this dataset uses")
    links = _ListDescr(nested="item", doc="list of links")
    metadata = _DictDescr(nested="item", doc="arbitrary metadata for this dataset")
    boson_config = BosonDescr(
        nested="item", doc="boson configuration for this dataset", default=BosonConfig()
    )
    version = _StringDescr(nested="item", doc="the version string for this dataset", default="")

    def __init__(self, **obj):
        o = {"class": "dataset"}
        # If this came from the dataset API, this needs to be built as an object
        if "item" not in obj:
            o["item"] = obj
            uid = obj.get("uid")
            if uid is not None:
                o["uid"] = uid
            o["name"] = obj.get("name", None)
            o["class"] = "dataset"
            o["domain"] = obj.get("domain", "*")
            o["category"] = obj.get("category", "*")
            o["type"] = obj.get("type", "*")
            o["description"] = obj.get("description", "")
            o["keywords"] = obj.get("keywords", [])
            o["metadata"] = obj.get("metadata", {})

            # geom from extent
            extent = obj.get("extent", {})
            spatial_extent = extent.get("spatial", None)
            if spatial_extent is not None:
                boxes = []
                for bbox in spatial_extent.get("bbox", []):
                    g = box(*bbox, ccw=False)
                    boxes.append(g)

                if len(boxes) == 1:
                    g = boxes[0]
                else:
                    g = MultiPolygon(boxes)

                self.geometry = g

        # Otherwise, parse as object
        else:
            obj["item"]["uid"] = obj["uid"]
            o = obj

        project = o.get("item", {}).get("project", None)

        super().__init__(**o)
        if project is not None:
            self.project = project

    def validate(self):
        res = self._client.post("datasets/validate", dataset=self.item, project=self.project.uid)

        try:
            raise_on_error(res)
        except Exception:
            try:
                js = res.json()["error"]
                print("Failed Validation:")
                print(js["detail"])
            except Exception:
                print(res.text)
            return False

        return True

    @property
    def object_class(self):
        return "Dataset"

    @object_class.setter
    def object_class(self, v):
        if v.lower() != "dataset":
            raise ValueError("shouldn't happen")
        self._set_item("class", "dataset")

    @property
    def bands(self):
        return self.item_assets

    def _ipython_display_(self, **kwargs):
        # Make this look like dataset list but with a single entry so one template can be used for both
        datasetList = {self.name: self}
        return geodesic_widgets.ObjectWidget(datasetList)._ipython_display_(**kwargs)

    def create(self) -> "Dataset":
        """
        Creates a new Dataset in Entanglement

        Returns:
            self

        Raises:
            requests.HTTPError: If this failed to create or if the dataset already exists

        """
        # Make sure the uid is either None or valid
        _ = self.uid

        body = {"overwrite": False, "dataset": self.item}

        res = raise_on_error(self._client.post("datasets", project=self.project.uid, **body))

        try:
            uids = res.json()["uids"]
        except KeyError:
            raise KeyError("no uids returned, something went wrong")

        if len(uids) > 1:
            raise ValueError("more datasets affected than requested, something unexpected happened")

        self._set_item("uid", uids[0])
        return self

    def save(self) -> "Dataset":
        """
        Updates an existing Dataset in Entanglement.

        Returns:
            self

        Raises:
            requests.HTTPError: If this failed to save.

        """
        # Make sure the uid is either None or valid
        try:
            self.uid
        except ValueError as e:
            raise e

        body = {"overwrite": True, "dataset": self.item}

        res = raise_on_error(self._client.post("datasets", project=self.project.uid, **body))
        try:
            uids = res.json().get("uids", [])
        except KeyError:
            raise KeyError("no uids returned, something went wrong")

        if len(uids) > 1:
            raise ValueError("more datasets affected than requested, something unexpected happened")
        elif len(uids) == 1:
            self._set_item("uid", uids[0])

        return self

    def _stac_client(self) -> STACAPI:
        # STAC Collection <=> Dataset name
        root = f"{boson_client._stub}/stac/{self.name}.{self.project.uid}/"

        return STACAPI(root)

    def search(
        self,
        bbox: Optional[List] = None,
        datetime: Union[List, Tuple] = None,
        limit: Optional[Union[bool, int]] = 10,
        page_size: Optional[int] = 500,
        intersects: Optional[object] = None,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        filter: Optional[Union[CQLFilter, dict]] = None,
        fields: Optional[dict] = None,
        sortby: Optional[dict] = None,
        method: str = "POST",
        extra_params: Optional[dict] = {},
    ):
        """Search the dataset for items.

        Search this service's OGC Features or STAC API.

        Args:
            bbox: The spatial extent for the query as a bounding box. Example: [-180, -90, 180, 90]
            datetime: The temporal extent for the query formatted as a list: [start, end].
            limit: The maximum number of items to return in the query. If None, will page through all results
            page_size: If retrieving all items, this page size will be used for the subsequent requests
            intersects: a geometry to use in the query
            collections: a list of collections to search
            ids: a list of feature/item IDs to filter to
            filter: a CQL2 filter. This is supported by most datasets but will not work for others.
            fields: a list of fields to include/exclude. Included fields should be prefixed by '+' \
                    and excluded fields by '-'. Alernatively, a dict with a 'include'/'exclude' lists may be provided
            sortby: a list of sortby objects, which are dicts containing "field" and "direction". \
                    Direction may be one of "asc" or "desc". Not supported by all datasets
            method: the HTTP method - POST is default and usually should be left alone unless a server doesn't support
            extra_params: a dict of additional parameters that will be passed along on the request.

        Returns:
            A :class:`geodesic.stac.FeatureCollection` with all items in the dataset matching the query.

        Examples:
            A query on the `sentinel-2-l2a` dataset with a given bounding box and time range. Additionally,
            you can apply filters on the parameters in the items

            >>> bbox = geom.bounds
            >>> date_range = (datetime.datetime(2020, 12,1), datetime.datetime.now())
            >>> ds.search(
            ...          bbox=bbox,
            ...          datetime=date_range,
            ...          filter=CQLFilter.lte("properties.eo:cloud_cover", 10.0)
            ... )

        """
        client = self._stac_client()

        # If limit is None, this will page through all results with the given page size (default 500)
        query_all = False
        if limit is None:
            limit = page_size
            query_all = True

        collection = client.search(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            intersects=intersects,
            collections=collections,
            ids=ids,
            filter=filter,
            fields=fields,
            sortby=sortby,
            method=method,
            extra_params=extra_params,
        )

        collection.dataset = self
        # If query_all, this cycles through all pages and reads into the feature collection.
        if query_all:
            collection.get_all()

        collection._is_stac = True
        return collection

    query = deprecated("1.0.0", "Dataset.query")(search)

    def get_pixels(
        self,
        *,
        bbox: list,
        datetime: Union[List, Tuple] = None,
        pixel_size: Optional[list] = None,
        shape: Optional[list] = None,
        pixel_dtype: Union[np.dtype, str] = np.float32,
        bbox_crs: str = "EPSG:4326",
        output_crs: str = "EPSG:3857",
        resampling: str = "nearest",
        no_data: Any = None,
        content_type: str = "raw",
        asset_bands: List[AssetBands] = [],
        filter: dict = {},
        compress: bool = True,
        bbox_srs: str = None,
        output_srs: str = None,
        input_nodata: Any = None,
        output_nodata: Any = None,
    ):
        """get pixel data or an image from this `Dataset`

        `get_pixels` gets requested pixels from a dataset by calling Boson. This method returns either a
        numpy array or the bytes of a image file (jpg, png, gif, or tiff). If the `content_type` is
        "raw", this will return a numpy array, otherwise it will return the requested image format as
        bytes that can be written to a file. Where possible, a COG will be returned for Tiff format,
        but is not guaranteed.

        Args:
            bbox: a bounding box to export as imagery (xmin, ymin, xmax, ymax)
            datetime: a start and end datetime to query against. Imagery will be filtered to between this range and mosaiced.
            pixel_size: a list of the x/y pixel size of the output imagery. This list needs to have length equal to the number of bands. This should be specified in the output spatial reference.
            shape: the shape of the output image (rows, cols). Either this or the `pixel_size` must be specified, but not both.
            pixel_dtype: a numpy datatype or string descriptor in numpy format (e.g. <f4) of the output. Most, but not all basic dtypes are supported.
            bbox_crs: the spatial reference of the bounding bbox, as a string. May be EPSG:<code>, WKT, Proj4, ProjJSON, etc.
            output_crs: the spatial reference of the output pixels.
            resampling: a string to select the resampling method.
            no_data: in the source imagery, what value should be treated as no data?
            content_type: the image format. Default is "raw" which sends raw image bytes that will \
                be converted into a numpy array. If "jpg", "gif", or "tiff", returns the bytes of an image \
                file instead, which can directly be written to disk.
            asset_bands: a list containing dictionaries with the keys "asset" and "bands". Asset \
                should point to an asset in the dataset, and "bands" should list band indices \
                (0-indexed) or band names.
            filter: a CQL2 JSON filter to filter images that will be used for the resulting output.
            compress: compress bytes when transfering. This will usually, but not always improve performance
            input_nodata (deprecated): in the source imagery, what value should be treated as no data?
            output_nodata (deprecated): what value should be set as the nodata value in the resulting dataset. Only meaningful for tiff outputs.
            bbox_srs (deprecated): the spatial reference of the bounding bbox, as a string. May be EPSG:<code>, WKT, Proj4, ProjJSON, etc.
            output_srs (deprecated): the spatial reference of the output pixels.

        Returns:
            a numpy array or bytes of an image file.

        """

        if pixel_size is None and shape is None:
            raise ValueError("must specify at least pixel_size or shape")
        elif pixel_size is not None and shape is not None:
            raise ValueError("must specify pixel_size or shape, but not both")

        if content_type not in ("raw", "jpeg", "jpg", "gif", "tiff", "png"):
            raise ValueError("content_type must be one of raw, jpeg, jpg, gif, tiff, png")

        if resampling not in _valid_resampling:
            raise ValueError(f'resampling must be one of {", ".join(_valid_resampling)}')

        if pixel_dtype in ["byte", "uint8"]:
            ptype = pixel_dtype
        else:
            ptype = np.dtype(pixel_dtype).name

        if bbox_srs is not None:
            warnings.warn(
                "bbox_srs is deprecated and will be removed in 1.0.0. Please use bbox_crs"
            )
            bbox_crs = bbox_srs
        if output_srs is not None:
            warnings.warn(
                "output_srs is deprecated and will be removed in 1.0.0. Please use output_crs"
            )
            output_crs = output_srs

        req = {
            "output_extent": bbox,
            "output_extent_spatial_reference": bbox_crs,
            "output_spatial_reference": output_crs,
            "pixel_type": ptype,
            "resampling_method": resampling,
            "content_type": content_type,
            "compress_response": compress,
        }

        if datetime is not None:
            req["time_range"] = [datetime_to_utc(parsedate(d)).isoformat() for d in datetime]

        if asset_bands:
            req["asset_bands"] = asset_bands

        if filter:
            req["filter"] = filter

        if pixel_size is not None:
            if isinstance(pixel_size, (list, tuple)):
                req["output_pixel_size"] = pixel_size
            elif isinstance(pixel_size, (int, float)):
                req["output_pixel_size"] = (pixel_size, pixel_size)

        if shape is not None:
            req["output_shape"] = shape

        if no_data is not None:
            req["no_data"] = no_data
        if input_nodata is not None:
            warnings.warn(
                "input_nodata is deprecated and will be removed in 1.0. Use nodata instead"
            )
            req["no_data"] = input_nodata
        if output_nodata is not None:
            warnings.warn("output_nodata is deprecated. This parameter will have not effect")

        if compress:
            boson_client.add_request_headers({"Accept-Encoding": "deflate, gzip"})

        try:
            res = raise_on_error(
                boson_client.post(f"raster/{self.name}.{self.project.uid}/pixels", **req)
            )
        except requests.HTTPError:
            # Try old endpoint for out of date clusters
            res = raise_on_error(
                boson_client.post(f"raster/{self.name}.{self.project.uid}/warp", **req)
            )

        raw_bytes = res.content

        if content_type == "raw":
            h = res.headers
            bands = int(h["X-Image-Bands"])
            rows = int(h["X-Image-Rows"])
            cols = int(h["X-Image-Columns"])

            x = np.frombuffer(raw_bytes, dtype=pixel_dtype)
            return x.reshape((bands, rows, cols))
        return raw_bytes

    warp = deprecated("1.0.0", "Dataset.warp")(get_pixels)

    def dataset_info(self) -> DatasetInfo:
        """returns information about this Dataset"""
        info = DatasetInfo(
            **raise_on_error(
                boson_client.get(f"dataset-info/{self.name}.{self.project.uid}/")
            ).json()
        )
        info.provider_config = self.boson_config
        return info

    def view(
        self,
        name: str,
        bbox: Optional[Union[List, Tuple]] = None,
        intersects: Optional[object] = None,
        datetime: Union[List, Tuple] = None,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        filter: Optional[Union[CQLFilter, dict]] = None,
        asset_bands: list = [],
        feature_limit: int = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = None,
        category: str = None,
        type: str = None,
        project: str = None,
        **kwargs,
    ) -> "Dataset":
        """creates a curated view of a ``Dataset``

        This method creates a new ``Dataset`` that is a "view" of an existing dataset. This allows the user
        to provide a set of persistent filters to a ``Dataset`` as a separate ``Object``. A view may also be
        saved in a different ``Project`` than the original. The applied filters affect both a query as
        well as the get_pixels. The final request processed will be the intersection of the view parameters
        with the query.

        Args:
            name: name of the view ``Dataset``
            bbox: The spatial extent for the query as a bounding box. Example: [-180, -90, 180, 90]
            intersects: a geometry to use in the query
            datetime: The temporal extent for the query formatted as a list: [start, end].
            collections: a list of collections to search
            ids: a list of feature/item IDs to filter to
            filter: a CQL2 filter. This is supported by most datasets but will not work for others.
            asset_bands: a list of asset/bands combinations to filter this ``Dataset`` to
            feature_limit: if specified, overrides the max_page_size of the this ``Dataset``
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            domain: domain of the resulting ``Object``
            category: category of the resulting ``Object``
            type: the type of the resulting ``Object``
            project: a new project to save this view to. If None, inherits from the parent ``Dataset``

        """
        if "extent" not in kwargs:
            kwargs["extent"] = self.extent

        collection = _stac_collection_from_kwargs(name, **kwargs)
        _remove_keys(collection, "id", "summaries", "stac_version")

        search_view = {}
        pixels_view = {}

        if bbox is not None:
            if len(bbox) != 4 and len(bbox) != 6:
                raise ValueError("bbox must be length 4 or 6")
            search_view["bbox"] = bbox
            pixels_view["bbox"] = bbox
            collection["extent"]["spatial"]["bbox"] = [bbox]

        if intersects is not None:
            # Geojson geometry OR feature
            if isinstance(intersects, dict):
                try:
                    g = shape(intersects)
                except (ValueError, AttributeError):
                    try:
                        g = shape(intersects["geometry"])
                    except Exception as e:
                        raise ValueError("could not determine type of intersection geometry") from e

            elif hasattr(intersects, "__geo_interface__"):
                g = intersects

            else:
                raise ValueError(
                    "intersection geometry must be either geojson or object with __geo_interface__"
                )

            search_view["intersects"] = g.__geo_interface__
            collection["extent"]["spatial"]["bbox"] = [g.bounds]

        if filter is not None:
            if not (isinstance(filter, dict) or isinstance(filter, dict)):
                raise ValueError("filter must be a valid CQL filter or dictionary")
            if isinstance(filter, dict):
                filter = CQLFilter(**filter)
            search_view["filter"] = filter
            pixels_view["filter"] = filter

        if datetime is not None:
            start = ".."
            end = ".."
            if len(datetime) == 1:
                start = end = _parse_date(datetime[0])
                pixels_view["datetime"] = [start]

            if len(datetime) == 2:
                start = _parse_date(datetime[0])
                end = _parse_date(datetime[1], index=1)
                pixels_view["datetime"] = [start, end]

            search_view["datetime"] = f"{start}/{end}"
            collection["extent"]["temporal"]["intervals"] = [[start, end]]

        if ids is not None:
            # unmarshaled using the STAC JSON marshaler, so it's "ids" not "feature_ids"
            search_view["ids"] = ids
            pixels_view["image_ids"] = ids
        if collections is not None:
            search_view["collections"] = collections
        if asset_bands is not None and len(asset_bands) > 0:
            pixels_view["asset_bands"] = asset_bands

        boson_cfg = BosonConfig(
            provider_name="view",
            properties={
                "provider": {
                    "dataset_name": self.name,
                    "project": self.project.uid,
                    "provider_config": self.boson_config,
                },
                "search_view": search_view,
                "pixels_view": pixels_view,
            },
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )
        if feature_limit is not None:
            boson_cfg.max_page_size = feature_limit

        if domain is None:
            domain = self.domain
        if category is None:
            category = self.category
        if type is None:
            type = self.type
        if project is None:
            project = self.project

        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api=self.data_api,
            item_type=self.item_type,
            boson_cfg=boson_cfg,
            domain=domain,
            category=category,
            type=type,
            project=project,
            **collection,
        )

    def union(
        self,
        name: str,
        others: List["Dataset"] = [],
        feature_limit: int = 1000,
        project: Optional[Union[Project, str]] = None,
        ignore_duplicate_fields: bool = False,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """creates a union of this dataset with a list of others

        Creates a new ``Dataset`` that is the ``union`` of this ``Dataset`` with a list of ``others``.
        If ``others`` is an empty list, this creates a union of a dataset with itself, which is essentially
        a virtual copy of the original endowed with any capabilities Boson adds.

        See: :py:func:`geodesic.entanglement.dataset.new_union_dataset`

        Args:
            name: the name of the new ``Dataset``
            others: a list of ``Datasets`` to ``union``
            feature_limit: the max size of a results page from a query/search
            project: the name of the project this will be assigned to
            ignore_duplicate_fields: if True, duplicate fields across providers will be ignored
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
        """

        return new_union_dataset(
            name=name,
            datasets=[self] + others,
            feature_limit=feature_limit,
            project=project,
            ignore_duplicate_fields=ignore_duplicate_fields,
            domain=domain,
            category=category,
            type=type,
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
            **kwargs,
        )

    def share(self, servicer: str, ttl: Union[pydatetime.timedelta, int, float] = None) -> Token:
        """
        Shares a dataset, producing a token that will allow unauthenticated users to run a proxied boson request

        Args:
            servicer: The name of the servicer to use in the boson request.
            ttl: The time in until the dataset's token should expire. Either a timedelta object or seconds
                 Defaults to -1 (no expiration) if not provided.

        Raises:
            requests.HTTPError: If the user is not permitted to access the dataset or if an error occurred

        Returns:
            a share token created by Ted and its corresponding data
        """
        name = self.name
        project = self.project.uid

        if isinstance(ttl, pydatetime.timedelta):
            ttl = int(ttl.total_seconds())

        if ttl is None:
            ttl = -1
        else:
            if isinstance(ttl, int):
                ttl = ttl
            else:
                raise ValueError("ttl must be an integer")

        params = {}
        params["dataset"] = name
        params["servicer"] = servicer
        params["project"] = project
        params["ttl"] = ttl

        res = raise_on_error(ted_client.post("", **params))
        return Token(**res.json())

    def share_as_arcgis_service(self, ttl: Union[pydatetime.timedelta, int, float] = None) -> Token:
        """Share a dataset as a GeoServices/ArcGIS service

        Args:
            ttl: The time in until the dataset's token should expire. Either a timedelta object or seconds
                 Defaults to -1 (no expiration) if not provided.

        Raises:
            requests.HTTPError: If the user is not permitted to access the dataset or if an error occurred

        Returns:
            a share token created by Ted and its corresponding data
        """

        return self.share(servicer="geoservices", ttl=ttl)

    def share_as_ogc_tiles_service(
        self, ttl: Union[pydatetime.timedelta, int, float] = None
    ) -> Token:
        """Share a dataset as a OGC Tiles service

        Args:
            ttl: The time in until the dataset's token should expire. Either a timedelta object or seconds
                 Defaults to -1 (no expiration) if not provided.

        Raises:
            requests.HTTPError: If the user is not permitted to access the dataset or if an error occurred

        Returns:
            a share token created by Ted and its corresponding data
        """

        return self.share(servicer="tiles", ttl=ttl)

    def command(self, command: str, **kwargs) -> dict:
        """issue a command to this dataset's provider

        Commands can be used to perform operations on a dataset such as reindexing. Most commands
        run in the background and will return immediately. If a command is successfully submitted,
        this should return a message `{"success": True}`, otherwise it will raise an exception with
        the error message.

        Args:
            command: the name of the command to issue. Providers supporting "reindex" will accept this command.
            **kwargs: additional arguments passed to this command.

        """
        return raise_on_error(
            boson_client.post(f"command/{self.name}.{self.project.uid}/{command}", **kwargs)
        ).json()

    def reindex(self, timeout: Union[pydatetime.timedelta, str] = None) -> dict:
        """issue a `reindex` command to this dataset's provider

        Reindexes a dataset. This will reindex the dataset in the background, and will return
        immediately. If the kicking off reindexing is successful, this will return a message
        `{"success": True}`, otherwise it will raise an exception with the error message.

        Args:
            timeout: the maximum time to wait for the reindexing to complete. If None, will use the
                      default timeout of 30 minutes.
        """
        if timeout is None:
            return self.command("reindex")

        class args(_APIObject):
            timeout = _TimeDeltaDescr()

        x = args(timeout=timeout)
        return self.command("reindex", **x)

    @staticmethod
    def from_snowflake_table(
        name: str,
        account: str,
        database: str,
        table: str,
        credential: str,
        schema: str = "public",
        warehouse: str = None,
        id_column: str = None,
        geometry_column: str = None,
        datetime_column: str = None,
        feature_limit: int = 8000,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs: dict,
    ) -> "Dataset":
        """create a ``Dataset`` from a Snowflake table.

        This method creates a new ``Dataset`` from an existing Snowflake table.

        Args:
            name: name of the ``Dataset``
            account: Snowflake account name
            database: Snowflake database that contains the table
            table: name of the Snowflake table
            credential: name of a credential to access table. Either basic auth or oauth2 refresh token are supported
            schema: Snowflake schema the table resides in
            warehouse: name of the Snowflake warehouse to use
            id_column: name of the column containing a unique identifier. Integer IDs preferred, but not required
            geometry_column: name of the column containing the primary geometry for spatial filtering.
            datetime_column: name of the column containing the primary datetime field for temporal filtering.
            feature_limit: max number of results to return in a single page from a search
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
        """
        collection = _stac_collection_from_kwargs(name, **kwargs)
        _remove_keys(collection, "id", "summaries", "stac_version")

        properties = dict(
            account=account,
            database=database,
            table=table,
            schema=schema,
        )
        if warehouse is not None:
            properties["warehouse"] = warehouse
        if id_column is not None:
            properties["id_column"] = id_column
        if geometry_column is not None:
            properties["geometry_column"] = geometry_column
        if datetime_column is not None:
            properties["datetime_column"] = datetime_column

        boson_cfg = BosonConfig(
            provider_name="snowflake",
            max_page_size=feature_limit,
            properties=properties,
            credentials={
                DEFAULT_CREDENTIAL_KEY: credential,
            },
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api="features",
            item_type="other",
            boson_cfg=boson_cfg,
            domain=domain,
            category=category,
            type=type,
            **collection,
        )

    @staticmethod
    def from_arcgis_item(
        name: str,
        item_id: str,
        arcgis_instance: str = "https://www.arcgis.com/",
        credential=None,
        layer_id: int = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        gis=None,
        **kwargs,
    ) -> "Dataset":
        """creates a new Dataset from an ArcGIS Online/Enterprise item

        Args:
            name: name of the Dataset to create
            item_id: the item ID of the ArcGIS Item Referenced
            arcgis_instance: the base url of the ArcGIS Online or Enterprise root. Defaults to AGOL, MUST be specified
                             for ArcGIS Enterprise instances
            credential: the name or uid of a credential required to access this. Currently, this must be the
                        client credentials of an ArcGIS OAuth2 Application. Public layers do not require credentials.
            layer_id: an integer layer ID to subset a service's set of layers.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            gis: the logged in `arcgis.gis.GIS` to use to access the metadata for this item. To access secure content,
                 if this is not specified, the active GIS is used.

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_arcgis_item(
            ...          name="my-dataset",
            ...          item_id="abc123efghj34234kxlk234joi",
            ...          credential="my-arcgis-creds"
            ... )
            >>> ds.save()
        """

        if arcgis_instance.endswith("/"):
            arcgis_instance = arcgis_instance[:-1]
        url = f"{arcgis_instance}/sharing/rest/content/items/{item_id}?f=pjson"

        if gis is None:
            gis = arcgis.env.active_gis

        js = _get_arcgis_url(url, gis=gis)

        # Get the server metadata for additional info that can be used to construct a initial dataset
        server_metadata = _get_arcgis_url(js["url"], gis=gis)
        try:
            server_metadata = server_metadata.json()
        except Exception:
            server_metadata = {}

        item_assets = {}
        if js["type"] == "Image Service":
            data_api = "stac"
            item_type = "raster"

            _get_esri_band_info(server_metadata, item_assets)
            _get_raster_function_assets(server_metadata, item_assets)

        elif js["type"] == "Feature Service":
            data_api = "features"
            item_type = "other"
        elif js["type"] == "Map Service":
            data_api = "features"
            item_type = "other"
        else:
            raise ValueError(f"unsupported ArcGIS Service Type '{js['type']}'")

        if js.get("licenseInfo") is not None and "termsofuse" in js.get("licenseInfo"):
            license = "https://goto.arcgis.com/termsofuse/viewtermsofuse"
        else:
            license = "(unknown)"

        spatial_extent = {"bbox": [[-180, -90, 180, 90]]}
        if "extent" in js:
            (x0, y0), (x1, y1) = js["extent"]

            spatial_extent = {"bbox": [[x0, y0, x1, y1]]}

        extent = {"spatial": spatial_extent, "temporal": {"interval": [[None, None]]}}

        providers = []
        if "owner" in js:
            providers.append({"name": js["owner"], "roles": ["processor"], "url": arcgis_instance})

        c = server_metadata.get("capabilities", [])
        supportsQuery = False
        supportsImage = False
        if "Catalog" in c or "Query" in c:
            supportsQuery = True
        if "Image" in c:
            supportsImage = True

        url = js["url"]
        if layer_id is not None:
            url += f"/{layer_id}"

        boson_cfg = BosonConfig(
            provider_name="geoservices",
            url=url,
            thread_safe=True,
            pass_headers=["X-Esri-Authorization"],
            properties={
                "supportsQuery": supportsQuery,
                "supportsImage": supportsImage,
            },
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        alias = js.get("title", name)
        keywords = js.get("tags", [])

        description = js.get("description")
        if description is None:
            description = js.get("snippet", "")

        credentials = {}
        if credential is not None:
            credentials = {DEFAULT_CREDENTIAL_KEY: credential}

        dataset = boson_dataset(
            name=name,
            alias=alias,
            description=description,
            keywords=keywords,
            license=license,
            data_api=data_api,
            item_type=item_type,
            extent=extent,
            boson_cfg=boson_cfg,
            providers=providers,
            item_assets=item_assets,
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **kwargs,
        )

        return dataset

    @staticmethod
    def from_arcgis_layer(
        name: str,
        url: str,
        arcgis_instance: str = "https://www.arcgis.com",
        credential=None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        gis=None,
        **kwargs,
    ) -> "Dataset":
        """creates a new Dataset from an ArcGIS Online/Enterprise Service URL

        Args:
            name: name of the Dataset to create
            url: the URL of the Feature, Image, or Map Server. This is the layer url, not the Service url.
                 Only the specified layer will be available to the dataset
            arcgis_instance: the base url of the ArcGIS Online or Enterprise root. Defaults to AGOL, MUST be specified
                             for ArcGIS Enterprise instances
            credential: the name or uid of a credential required to access this. Currently, this must be the
                        client credentials of an ArcGIS OAuth2 Application. Public layers do not require credentials.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            gis: the logged in `arcgis.gis.GIS` to use to access the metadata for this item. To access secure content,
                 if this is not specified, the active GIS is used.

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_arcgis_layer(
            ...          name="my-dataset",
            ...          url="https://services9.arcgis.com/ABC/arcgis/rest/services/SomeLayer/FeatureServer/0",
            ...          credential="my-arcgis-creds"
            ... )
            >>> ds.save()
        """

        if url.endswith("/"):
            url = url[:-1]

        layer_id = url.split("/")[-1]
        try:
            layer_id = int(layer_id)
        except ValueError:
            raise ValueError(
                "invalid url, must be of the form https://<host>/.../LayerName/FeatureServer/<layer_id>"
                f"got {url}"
            )

        url = "/".join(url.split("/")[:-1])
        return Dataset.from_arcgis_service(
            name=name,
            url=url,
            arcgis_instance=arcgis_instance,
            credential=credential,
            layer_id=layer_id,
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
            domain=domain,
            category=category,
            type=type,
            gis=gis,
            **kwargs,
        )

    @staticmethod
    def from_arcgis_service(
        name: str,
        url: str,
        arcgis_instance: str = "https://www.arcgis.com",
        credential=None,
        layer_id: int = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        gis=None,
        **kwargs,
    ) -> "Dataset":
        """creates a new Dataset from an ArcGIS Online/Enterprise Service URL

        Args:
            name: name of the Dataset to create
            url: the URL of the Feature, Image, or Map Server. This is not the layer url, but the Service url.
                 Layers will be enumerated and all accessible from this dataset.
            arcgis_instance: the base url of the ArcGIS Online or Enterprise root. Defaults to AGOL, MUST be specified
                             for ArcGIS Enterprise instances
            credential: the name or uid of a credential required to access this. Currently, this must be the
                        client credentials of an ArcGIS OAuth2 Application. Public layers do not require credentials.
            layer_id: an integer layer ID to subset a service's set of layers.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            gis: the logged in `arcgis.gis.GIS` to use to access the metadata for this item. To access secure content,
                 if this is not specified, the active GIS is used.

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_arcgis_service(
            ...          name="my-dataset",
            ...          url="https://services9.arcgis.com/ABC/arcgis/rest/services/SomeLayer/FeatureServer",
            ...          credential="my-arcgis-creds"
            ... )
            >>> ds.save()
        """

        if url.endswith("/"):
            url = url[:-1]
        if not url.endswith("Server"):
            raise ValueError("url must end with ImageServer, FeatureServer, or MapServer")
        server_metadata = _get_arcgis_url(url, gis=gis)

        # Get the name, if the name doesn't exist, get the serviceItemId and build using from_arcgis_item
        dataset_alias = server_metadata.get("name")
        if dataset_alias is None:
            item_id = server_metadata.get("serviceItemId")
            # No way to find out the alias/human readable name, so set to the provided dataset name
            if item_id is None:
                dataset_alias = name
            else:
                return Dataset.from_arcgis_item(
                    name=name,
                    item_id=item_id,
                    arcgis_instance=arcgis_instance,
                    credential=credential,
                    layer_id=layer_id,
                    middleware=middleware,
                    cache=cache,
                    tile_options=tile_options,
                    domain=domain,
                    category=category,
                    type=type,
                    gis=gis,
                )

        item_assets = {}

        if layer_id is not None:
            url += f"/{layer_id}"

        if "ImageServer" in url:
            data_api = "stac"
            item_type = "raster"

            _get_esri_band_info(server_metadata, item_assets)
            _get_raster_function_assets(server_metadata, item_assets)

        elif "FeatureServer" in url:
            data_api = "features"
            item_type = "other"
        elif "MapServer" in url:
            data_api = "features"
            item_type = "other"
        else:
            raise ValueError("unsupported service type")

        license = "(unknown)"

        spatial_extent = {"bbox": [[-180, -90, 180, 90]]}

        e = {}
        if "extent" in server_metadata:
            e = server_metadata["extent"]
        elif "fullExtent" in server_metadata:
            e = server_metadata["fullExtent"]

        x0 = e.get("xmin", -180.0)
        y0 = e.get("ymin", -90.0)
        x1 = e.get("xmax", 180.0)
        y1 = e.get("ymax", 90.0)

        sr = e.get("spatialReference", {})
        wkid = sr.get("latestWkid", sr.get("wkid", 4326))

        if wkid != 4326:
            p0 = pyproj.Proj(f"epsg:{wkid}", preserve_units=True)
            p1 = pyproj.Proj("epsg:4326", preserve_units=True)
            t = pyproj.Transformer.from_proj(p0, p1, always_xy=True)
            lo0, la0 = t.transform(x0, y0)
            lo1, la1 = t.transform(x1, y1)

        else:
            lo0, la0, lo1, la1 = x0, y0, x1, y1

        spatial_extent = {"bbox": [[lo0, la0, lo1, la1]]}

        extent = {"spatial": spatial_extent, "temporal": {"interval": [[None, None]]}}

        c = server_metadata["capabilities"]
        supportsQuery = False
        supportsImage = False
        if "Catalog" in c or "Query" in c:
            supportsQuery = True
        if "Image" in c:
            supportsImage = True

        boson_cfg = BosonConfig(
            provider_name="geoservices",
            url=url,
            thread_safe=True,
            pass_headers=["X-Esri-Authorization"],
            properties={
                "supportsQuery": supportsQuery,
                "supportsImage": supportsImage,
            },
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        credentials = {}
        if credential is not None:
            credentials = {DEFAULT_CREDENTIAL_KEY: credential}

        dataset = boson_dataset(
            name=name,
            alias=server_metadata.get("name", name),
            description=server_metadata.get("description", ""),
            keywords=[],
            license=license,
            data_api=data_api,
            item_type=item_type,
            extent=extent,
            boson_cfg=boson_cfg,
            item_assets=item_assets,
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **kwargs,
        )

        return dataset

    @staticmethod
    def from_stac_collection(
        name: str,
        url: str,
        credential=None,
        item_type: str = "raster",
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """Create a new Dataset from a STAC Collection

        Args:
            name: name of the Dataset to create
            url: the url to the collection (either STAC API or OGC API: Features)
            credential: name or uid of the credential to access the API
            item_type: what type of items does this contain? "raster" for raster data, "features" for features, other
                       types, such as point_cloud may be specified, but doesn't alter current internal functionality.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_stac_collection(
            ...          name="landsat-c2l2alb-sr-usgs",
            ...          url="https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l2alb-sr"
            ...)
            >>> ds.save()
        """

        if url.endswith("/"):
            url = url[:-1]

        if "collections" not in url:
            raise ValueError("url must be of the form {STAC_ROOT}/collections/:collectionId")

        rs = stac_root_re.match(url)

        try:
            root = rs.group(1)
        except Exception:
            raise ValueError("invalid URL")

        res = get_client().get(url)

        try:
            stac_collection = res.json()
        except Exception:
            raise ValueError("unable to get service metadata. (did you enter the correct url?)")

        stac_extent = stac_collection.get("extent", {})
        spatial_extent = stac_extent.get("spatial", {})
        bbox = spatial_extent.get("bbox", [[-180.0, -90.0, 180.0, 90.0]])
        temporal_extent = stac_extent.get("temporal", {})
        interval = temporal_extent.get("interval", [[None, None]])

        extent = {
            "spatial": {"bbox": bbox},
            "temporal": {"interval": interval},
        }

        if interval[0][1] is None:
            interval[0][1] = pydatetime.datetime(2040, 1, 1).strftime("%Y-%m-%dT%H:%M:%SZ")

        item_assets = stac_collection.get("item_assets", {})

        links = stac_collection.get("links", [])
        extensions = stac_collection.get("stac_extensions", [])
        providers = stac_collection.get("providers", [])

        keywords = stac_collection.get("keywords", [])
        keywords += ["boson"]

        boson_cfg = BosonConfig(
            provider_name="stac",
            url=root,
            thread_safe=True,
            pass_headers=[],
            properties={"collection": stac_collection["id"]},
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        data_api = "stac"

        credentials = {}
        if credential is not None:
            credentials = {DEFAULT_CREDENTIAL_KEY: credential}

        dataset = boson_dataset(
            name=name,
            alias=stac_collection.get("title", name),
            description=stac_collection.get("description", ""),
            keywords=keywords,
            license=stac_collection.get("license", ""),
            data_api=data_api,
            item_type=item_type,
            extent=extent,
            boson_cfg=boson_cfg,
            providers=providers,
            links=links,
            item_assets=item_assets,
            stac_extensions=extensions,
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **kwargs,
        )

        return dataset

    @staticmethod
    def from_bucket(
        name: str,
        url: str,
        pattern: str = None,
        region: str = None,
        datetime_field: str = None,
        start_datetime_field: str = None,
        end_datetime_field: str = None,
        oriented: bool = False,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """Creates a new Dataset from a Cloud Storage Bucket (S3/GCP/Azure)

        Args:
            name: name of the Dataset to create
            url: the url to the bucket, including the prefix (ex. s3://my-bucket/myprefix, gs://my-bucket/myprefix, ...)
            pattern: a regex to filter for files to index
            region: for S3 buckets, the region where the bucket is
            datetime_field: the name of the metadata key on the file to find a timestamp
            start_datetime_field: the name of the metadata key on the file to find a start timestamp
            end_datetime_field: the name of the metadata key on the file to find an end timestamp
            oriented: Is this oriented imagery? If so, EXIF data will be parsed for geolocation. Anything missing
                      location info will be dropped.
            credential: the name or uid of the credential to access the bucket.
            middleware: configure any boson middleware to be applied to the new dataset.
            kwargs: other metadata that will be set on the Dataset, such as description, alias, etc

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_bucket(
            ...          name="bucket-dataset",
            ...          url="s3://my-bucket/myprefix",
            ...          pattern=r".*\\.tif",
            ...          region="us-west-2",
            ...          datetime_field="TIFFTAG_DATETIME",
            ...          oriented=False,
            ...          credential="my-iam-user",
            ...          description="my dataset is the bomb"
            ...)
            >>> ds.save()

        """

        info = {
            "name": name,
            "alias": kwargs.get("alias", name),
            "description": kwargs.get("description", "(no description)"),
            "keywords": kwargs.get("keywords", []),
            "license": kwargs.get("license", "unknown"),
            "data_api": kwargs.get("data_api", "stac"),
            "item_type": kwargs.get("item_type", "raster"),
            "extent": kwargs.get(
                "extent",
                {
                    "spatial": {"bbox": [[-180.0, -90.0, 180.0, 90.0]]},
                    "temporal": {"interval": [[None, None]]},
                },
            ),
            "providers": kwargs.get("providers", []),
            "item_assets": kwargs.get("item_assets", {}),
            "links": kwargs.get("links", []),
            "stac_extensions": kwargs.get("stac_extensions", ["item_assets"]),
        }
        if credential is not None:
            info["credentials"] = {STORAGE_CREDENTIAL_KEY: credential}

        if pattern is not None:
            try:
                re.compile(pattern)
            except Exception:
                raise ValueError(f"invalid pattern '{pattern}'")

        properties = {"alias": info["alias"], "description": info["description"]}
        if pattern is not None:
            properties["pattern"] = pattern
        if datetime_field is not None:
            properties["datetime_field"] = datetime_field
        if start_datetime_field is not None:
            properties["start_datetime_field"] = start_datetime_field
        if end_datetime_field is not None:
            properties["end_datetime_field"] = end_datetime_field
        if region is not None:
            properties["region"] = region

        boson_cfg = BosonConfig(
            provider_name="bucket",
            url=url,
            properties=properties,
            thread_safe=True,
            max_page_size=500,
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        return boson_dataset(
            boson_cfg=boson_cfg, domain=domain, category=category, type=type, **info
        )

    @staticmethod
    def from_google_earth_engine(
        name: str,
        asset: str,
        credential: str,
        folder: str = "projects/earthengine-public/assets",
        url: str = "https://earthengine-highvolume.googleapis.com",
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """Creates a new Dataset from a Google Earth Engine Asset

        Args:
            name: name of the Dataset to create
            asset: the asset in GEE to use (ex. 'LANDSAT/LC09/C02/T1_L2')
            credential: the credential to access this, a Google Earth Engine GCP Service Account. Future will allow
                        the use of a oauth2 refresh token or other.
            folder: by default this is the earth engine public, but you can specify another folder if needed to point
                    to legacy data or personal projects.
            url: the GEE url to use, defaults to the recommended high volume endpoint.
            kwargs: other metadata that will be set on the Dataset, such as description, alias, etc
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_google_earth_engine(
            ...          name="landsat-9-c2-gee",
            ...          asset="s3://my-bucket/myprefixLANDSAT/LC09/C02/T1_L2",
            ...          credential="google-earth-engine-svc-account",
            ...          description="my dataset is the bomb"
            ...)
            >>> ds.save()

        """

        item_assets = {"image": Asset(title="image", description="image data for this dataset")}

        info = {
            "name": name,
            "alias": kwargs.get("alias", name),
            "description": kwargs.get("description", "(no description)"),
            "keywords": kwargs.get("keywords", []),
            "license": "https://earthengine.google.com/terms/",
            "data_api": kwargs.get("data_api", "stac"),
            "item_type": kwargs.get("item_type", "raster"),
            "extent": kwargs.get(
                "extent",
                {
                    "spatial": {"bbox": [[-180.0, -90.0, 180.0, 90.0]]},
                    "temporal": {"interval": [[None, None]]},
                },
            ),
            "providers": kwargs.get(
                "providers",
                [
                    {
                        "name": "Google",
                        "description": "Google provides Earth Engine for Google Earth Engine combines a multi-petabyte "
                        "catalog of satellite imagery and geospatial datasets with planetary-scale analysis "
                        "capabilities. Scientists, researchers, and developers use Earth Engine to detect "
                        "changes, map trends, and quantify differences on the Earth's surface. Earth Engine "
                        "is now available for commercial use, and remains free for acadecmic and research use.",
                        "url": "https://earthengine.google.com/",
                        "roles": ["host", "processor", "producer", "licensor"],
                    }
                ],
            ),
            "item_assets": kwargs.get("item_assets", item_assets),
            "links": kwargs.get("links", []),
            "stac_extensions": kwargs.get("stac_extensions", ["item_assets"]),
            "credentials": {DEFAULT_CREDENTIAL_KEY: credential},
        }

        try:
            if not ee.data._credentials:
                ee.Initialize()
            _parse_earth_engine_data(asset, info, **kwargs)
        except ImportError:
            pass

        boson_cfg = BosonConfig(
            provider_name="google-earth-engine",
            url=url,
            thread_safe=True,
            max_page_size=500,
            properties={"asset": asset, "folder": folder},
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        return boson_dataset(
            boson_cfg=boson_cfg, domain=domain, category=category, type=type, **info
        )

    @staticmethod
    def from_elasticsearch_index(
        name: str,
        url: str,
        index_pattern: str,
        credential: str = None,
        storage_credential: str = None,
        datetime_field: str = "properties.datetime",
        geometry_field: str = "geometry",
        geometry_type: str = "geo_shape",
        id_field: str = "_id",
        data_api: str = "features",
        item_type: str = "other",
        feature_limit: int = 2000,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """create a new Dataset from an elasticsearch index containing geojson features or STAC items

        Args:
            name: name of the Dataset to create
            url: the DNS name or IP of the elasticsearch host to connect to.
            index_pattern: an elasticsearch index name or index pattern
            credential: name of the Credential object to use. Currently, this only supports basic auth
                (username/password).
            storage_credential: the name of the Credential object to use for storage if any of the data
                referenced in the index requires a credential to access (e.g. cloud storage for STAC)
            datetime_field: the field that is used to search by datetime in the elasticserach index.
            geometry_field: the name of the field that contains the geometry
            geometry_type: the type of the geometry field, either geo_shape or geo_point
            id_field: the name of the field to use as an ID field
            data_api: the data API, either 'stac' or 'features'
            item_type: the type of item. If it's a stac data_api, then it should describe what the data is
            feature_limit: the max number of features the service will return per page.
            middleware: configure any boson middleware to be applied to the new dataset.
            **kwargs: other arguments that will be used to create the collection and provider config.

        Returns:
            A new Dataset. Must call .save() for it to be usable.
        """

        collection = _stac_collection_from_kwargs(name, **kwargs)
        elastic_config = dict(
            disable_retry=kwargs.get("retries", False),
            enable_debug_logger=kwargs.get("enable_debug_logger", False),
            enable_compatibility_mode=kwargs.get("enable_compatibility_mode", False),
            insecure=kwargs.get("insecure", True),
            max_retries=kwargs.get("max_retries", 5),
            feature_limit=feature_limit,
            date_field=datetime_field,
            index_pattern=index_pattern,
            geometry_field=geometry_field,
            geometry_type=geometry_type,
            id_field=id_field,
            collection=dict(**collection),
        )
        elastic_config.update(kwargs)

        credentials = {}
        if credential is not None:
            credentials[DEFAULT_CREDENTIAL_KEY] = credential
        if storage_credential is not None:
            credentials[STORAGE_CREDENTIAL_KEY] = storage_credential

        _remove_keys(collection, "id", "summaries", "stac_version")
        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api=data_api,
            item_type=item_type,
            boson_cfg=BosonConfig(
                provider_name="elastic",
                url=url,
                max_page_size=feature_limit,
                properties=elastic_config,
                middleware=middleware,
                cache=cache,
                tile_options=tile_options,
            ),
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **collection,
        )

    @staticmethod
    def from_csv(
        name: str,
        url: str,
        index_data: bool = True,
        crs: str = "EPSG:4326",
        x_field: str = "CoordX",
        y_field: str = "CoordY",
        z_field: str = "CoordZ",
        geom_field: str = "WKT",
        feature_limit: int = 1000,
        region: str = None,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """create a new Dataset from a CSV file in cloud storage

        Args:
            name: name of the Dataset to create
            url: the URL/URI of the data. Can be a cloud storage URI such as s3://<bucket>/key, gs://
            index_data: if true, the data will be copied and spatially indexed for more efficient queries
            crs: a string coordinate reference for the data
            (x/y/z)_field: the field name for the x/y/z fields
            geom_field: the field name containing the geometry in well known text (WKT) or hex encoded well known binary
                (WKB).
            feature_limit: the max number of features this will return per page
            region: for S3 buckets, the region where the bucket is
            credential: the name of the credential object needed to access this data.
            middleware: configure any boson middleware to be applied to the new dataset.

        """

        csv = dict(x_field=x_field, y_field=y_field, z_field=z_field, geom_field=geom_field)

        return Dataset.from_tabular_data(
            name,
            url,
            index_data=index_data,
            crs=crs,
            feature_limit=feature_limit,
            region=region,
            credential=credential,
            csv=csv,
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
            domain=domain,
            category=category,
            type=type,
            **kwargs,
        )

    @staticmethod
    def from_tabular_data(
        name: str,
        url: str,
        index_data: bool = True,
        crs: str = "EPSG:4326",
        feature_limit: int = 1000,
        region: str = None,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """create a new Dataset from a vector file in cloud storage.

        This can be a Shapefile, GeoJSON Feature Collection, FlatGeobuf, and several others

        Args:
            name: name of the Dataset to create
            url: the URL/URI of the data. Can be a cloud storage URI such as s3://<bucket>/key, gs://
            index_data: if true, the data will be copied and spatially indexed for more efficient queries
            crs: a string coordinate reference for the data
            feature_limit: the max number of features this will return per page
            region: for S3 buckets, the region where the bucket is
            credential: the name of the credential object needed to access this data.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
        """

        collection = _stac_collection_from_kwargs(name, **kwargs)

        credentials = {}
        if credential is not None:
            credentials = {STORAGE_CREDENTIAL_KEY: credential}

        properties = dict(index_data=index_data, crs=crs, region=region)
        csv = kwargs.pop("csv", None)
        if csv is not None:
            properties["csv"] = csv
        if region is not None:
            properties["region"] = region

        _remove_keys(collection, "id", "summaries", "stac_version")
        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api="features",
            item_type="other",
            boson_cfg=BosonConfig(
                provider_name="tabular",
                url=url,
                max_page_size=feature_limit,
                properties=properties,
                middleware=middleware,
                cache=cache,
                tile_options=tile_options,
            ),
            domain=domain,
            category=category,
            type=type,
            credentials=credentials,
            **collection,
        )

    @staticmethod
    def from_geoparquet(
        name: str,
        url: str,
        feature_limit: int = 1000,
        datetime_field: str = "datetime",
        return_geometry_properties: bool = False,
        expose_partitions_as_layer: bool = True,
        update_existing_index: bool = True,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """creates a dataset from Hive-partitioned GeoParquet files in cloud storage

        Hive-partition GeoParquet is a particular convention typically used when writing data out
        from a parallel process (such as Tesseract or Apache Spark) or when the individual file
        sizes or row counts are too large. This provider indexes these partitions spatially to
        optimize query performance. Hive partitioned parquet is organized like this and we require
        this structure:

        prefix/<root>.parquet
            /key=value_1/<partition-00001>.parquet
            /key=value_2/<partition-00002>.parquet
            /...
            /key=value_m/<partition-n>.parquet

        "root" and "partition-xxxxx" can be whatever provided they both have the parquet suffix.
        Any number oof key/value pairs are allowed in Hive Partitioned data. This can also point
        to a single parquet file.

        Args:
            name: name of the Dataset to create
            url: the path to the <root>.parquet. Format depends on the storage backend.
            feature_limit: the max number of features that this provider will allow returned by a
                single query.
            datetime_field: if the data is time enabled, this is the name of the datetime field.
            return_geometry_properties: if True, will compute and return geometry properties along with
                the features.
            expose_partitions_as_layer: this will create a collection/layer in this Dataset that simply
                has the partition bounding box and count of features within. Can be used as a simple heatmap
            update_existing_index: if the data has been indexed in our scheme by a separate process, set to False
                to use that instead, otherwise this will index the parquet data in the bucket before you
                are able to query it.
            credential: the name of the credential to access the data in cloud storage.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            **kwargs: additional arguments that will be used to create the STAC collection, Dataset description
                Alias, etc.

        """
        if not url.endswith(".parquet"):
            raise ValueError('url must end with ".parquet"')

        collection = _stac_collection_from_kwargs(name, **kwargs)

        credentials = {}
        if credential is not None:
            credentials = {STORAGE_CREDENTIAL_KEY: credential}

        data_api = "features"
        item_type = "other"

        _remove_keys(collection, "id", "summaries", "stac_version")
        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api=data_api,
            item_type=item_type,
            boson_cfg=BosonConfig(
                provider_name="geoparquet",
                url=url,
                max_page_size=feature_limit,
                properties={
                    "datetime_field": datetime_field,
                    "expose_partitions_as_layer": expose_partitions_as_layer,
                    "update_existing_index": update_existing_index,
                    "return_geometry_properties": return_geometry_properties,
                },
                middleware=middleware,
                cache=cache,
                tile_options=tile_options,
            ),
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **collection,
        )

    @staticmethod
    def from_remote_provider(
        name: str,
        url: str,
        data_api: str = "features",
        transport_protocol: str = "http",
        feature_limit: int = 2000,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """Creates a dataset from a server implementing the Boson remote provider interface

        The Boson Remote Provider interface may be implemented using the
        Boson Python SDK (https://pypi.org/project/boson-sdk/). The provider must
        be hosted somewhere and this connects Boson to a remote provider.

        Remote Providers may either implement the Search or the Pixels endpoint (or both).

        Args:
            name: name of the Dataset to create
            url: URL of the server implementing the interface
            data_api: either 'features' or 'raster'.
            transport_protocol: either 'http' or 'grpc'
            credential: the name of the credential to access the api.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            **kwargs: additional arguments that will be used to create the STAC collection, Dataset description
                Alias, etc.
        """

        collection = _stac_collection_from_kwargs(name, **kwargs)

        credentials = {}
        if credential is not None:
            credentials = {DEFAULT_CREDENTIAL_KEY: credential}

        data_api = "features"
        item_type = "other"

        _remove_keys(collection, "id", "summaries", "stac_version")
        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api=data_api,
            item_type=item_type,
            boson_cfg=BosonConfig(
                provider_name="remote",
                url=url,
                max_page_size=feature_limit,
                properties={"protocol": transport_protocol},
                middleware=middleware,
                cache=cache,
                tile_options=tile_options,
            ),
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **collection,
        )


def _stac_collection_from_kwargs(name: str, **kwargs) -> dict:
    return dict(
        id=name,
        title=kwargs.get("alias", name),
        description=kwargs.get("description", "(no description)"),
        keywords=kwargs.get("keywords", []),
        license=kwargs.get("license", ""),
        extent=kwargs.get(
            "extent",
            {
                "spatial": {"bbox": [[-180.0, -90.0, 180.0, 90.0]]},
                "temporal": {"interval": [[None, None]]},
            },
        ),
        providers=kwargs.get("providers", []),
        item_assets=kwargs.get("item_assets", {}),
        links=kwargs.get("links", []),
        stac_extensions=kwargs.get("stac_extensions", []),
        summaries=kwargs.get("summaries", {}),
        stac_version="1.0.0",
    )


def _parse_earth_engine_data(asset: str, info: dict, **kwargs):
    gee_info = {}
    try:
        item = ee.ImageCollection(asset).limit(1)
        gee_info = item.getInfo()
    except Exception as e:
        if "ImageCollection, found 'Image'" in str(e):
            item = ee.Image(asset)
        else:
            item = ee.FeatureCollection(asset).limit(1)
        gee_info = item.getInfo()

    gee_type = gee_info.get("type")

    if gee_type is None:
        return

    properties = gee_info.get("properties", {})
    if properties.get("description") is not None and kwargs.get("description") is None:
        info["description"] = properties.get("description")

    features = gee_info.get("features", [])
    if len(features) == 0:
        return

    feature = features[0]
    item_assets = {}
    if gee_type == "ImageCollection":
        bands = feature["bands"]
        for band in bands:
            asset_name = band["id"]
            item_assets[asset_name] = Asset(
                title=asset_name, type="image/tiff; application=geotiff"
            )

        item_assets["image"] = Asset(
            title="image",
            description="image data for this dataset",
            type="image/tiff; application=geotiff",
        )
        info["item_assets"] = item_assets


def boson_dataset(
    *,
    name: str,
    alias: str,
    description: str,
    keywords: List[str],
    license: str,
    data_api: str,
    item_type: str,
    extent: dict,
    boson_cfg: "BosonConfig",
    providers: list = [],
    item_assets: dict = {},
    links: list = [],
    stac_extensions: list = [],
    credentials={},
    domain: str = "*",
    category: str = "*",
    type: str = "*",
    project: Project = None,
) -> Dataset:
    boson_cfg.credentials = credentials

    if project is None:
        project = get_active_project().uid
    elif isinstance(project, str):
        project = get_project(project).uid
    else:
        project = project.uid

    dataset = Dataset(
        name=name,
        alias=alias,
        description=description,
        keywords=keywords,
        license=license,
        data_api=data_api,
        item_type=item_type,
        extent=extent,
        boson_config=boson_cfg,
        providers=providers,
        item_assets=item_assets,
        links=links,
        stac_extensions=stac_extensions,
        version="v0.0.1",
        created=pydatetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        updated=pydatetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        services=["boson"],
        object_class="dataset",
        domain=domain,
        category=category,
        type=type,
        project=project,
    )

    return dataset


def _remove_keys(d: dict, *keys) -> None:
    for key in keys:
        d.pop(key)


def parsedate(dt):
    try:
        return parse(dt)
    except TypeError:
        return dt


class DatasetList(_APIObject):
    def __init__(self, datasets, ids=[]):
        self.ids = ids
        if len(ids) != len(datasets):
            self.ids = [dataset.name for dataset in datasets]
        for dataset in datasets:
            self._set_item(dataset.name, dataset)

    def __getitem__(self, k) -> Dataset:
        if isinstance(k, str):
            return super().__getitem__(k)
        elif isinstance(k, int):
            did = self.ids[k]
            return super().__getitem__(did)
        else:
            raise KeyError("invalid key")

    def _ipython_display_(self, **kwargs):
        return geodesic_widgets.ObjectWidget(self)._ipython_display_(**kwargs)


class ItemAssets(dict):
    def __init__(self, item_assets=None, ds_name=None):
        self.update(item_assets)
        self._ds_name = ds_name

    def _ipython_display_(self, **kwargs):
        return geodesic_widgets.ItemAssetsWidget(self)._ipython_display_(**kwargs)


class _DatasetDescr(_BaseDescr):
    """A geodesic Dataset descriptor

    Returns a Dataset object, sets the Dataset name on the base object. Dataset
    MUST exist in Entanglement, in a user accessible project/graph.

    """

    def __init__(self, project=None, **kwargs):
        super().__init__(**kwargs)
        self.project = project

    def _get(self, obj: object, objtype=None) -> dict:
        # Try to get the private attribute by name (e.g. '_dataset')
        return getattr(obj, self.private_name, None)

    def _set(self, obj: object, value: object) -> None:
        dataset = self.get_dataset(value)

        # Reset the private attribute (e.g. "_dataset") to None
        setattr(obj, self.private_name, dataset)

        if self.project is not None:
            self.project.__set__(obj, dataset.project)

        self._set_object(obj, dataset.name)

    def get_dataset(self, value):
        # If the Dataset was set, we need to validate that it exists and the user has access
        dataset_name = None
        if isinstance(value, str):
            dataset_name = value
            project = get_active_project().uid
        else:
            dataset = Dataset(**value)
            dataset_name = dataset.name
            project = dataset.project.uid

        try:
            return get_dataset(dataset_name, project=project)
        except Exception:
            # Try to get from 'global'
            try:
                return get_dataset(dataset_name, project="global")
            except Exception as e:
                projects = set([project, "global"])
                raise ValueError(
                    f"dataset '{dataset_name}' does not exist in ({', '.join(projects)}) or"
                    " user doesn't have access"
                ) from e

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, (Dataset, str, dict)):
            raise ValueError(f"'{self.public_name}' must be a Dataset or a string (name)")

        # If the Dataset was set, we need to validate that it exists and the user has access
        self.get_dataset(value)


def _get_esri_band_info(server_metadata: dict, item_assets: dict):
    eo_bands = []
    for band_name in server_metadata.get("bandNames", []):
        eo_bands.append(
            {
                "name": band_name,
                "description": "an image service band",
            }
        )

    asset = Asset(
        **{
            "title": "image",
            "type": "application/octet-stream",
            "description": "image data for this image service",
            "roles": ["dataset"],
        }
    )
    if len(eo_bands) > 0:
        asset["eo:bands"] = eo_bands

    item_assets["image"] = asset


def _get_raster_function_assets(server_metadata: dict, item_assets: dict):
    for rasterFunctionInfo in server_metadata.get("rasterFunctionInfos", []):
        name = rasterFunctionInfo.get("name", "None")
        if name != "None":
            description = rasterFunctionInfo.get("description", "")
            item_assets[name] = Asset(
                **{
                    "title": name,
                    "type": "application/octet-stream",
                    "description": description,
                    "roles": ["dataset"],
                }
            )


def _get_arcgis_url(url: str, gis: "arcgis.GIS" = None) -> dict:
    js = {}

    if gis is None:
        try:
            gis = arcgis.env.active_gis
        except Exception:
            pass
        else:
            gis = arcgis.GIS()

    # no GIS provided, use the geodesic client
    if gis is None:
        res = get_client().get(url, f="pjson")
        try:
            js = raise_on_error(res).json()
        except Exception:
            raise ValueError(
                "unable to get item info. (did you enter the correct arcgis_instance?)"
            )
    else:
        try:
            js = gis._con.get(url)
        except Exception as e:
            raise ValueError(
                "unable to get item info, ensure you are logged into ArcGIS through"
                " the ArcGIS API for Python"
            ) from e

    return js
