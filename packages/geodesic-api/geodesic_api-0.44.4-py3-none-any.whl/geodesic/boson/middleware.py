from geodesic.bases import _APIObject
from geodesic.descriptors import _ListDescr, _StringDescr, _DictDescr
from geodesic.boson.asset_bands import AssetBands
from typing import List, Union

# Middleware types
SEARCH_FILTER_CQL2 = "cql2"
SEARCH_FILTER_SPATIAL = "spatial"
SEARCH_FILTER_DATETIME = "datetime"
SEARCH_TRANSFORM_RENAME_FIELDS = "rename-fields"
SEARCH_TRANSFORM_COMBINE_FIELDS = "combine-fields"
PIXELS_TRANSFORM_COLORMAP = "colormap"
PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS = "default_asset_bands"


class _Middleware(_APIObject):
    _limit_setitem = ("type", "properties")
    type = _StringDescr(
        doc="type of middleware to apply to a provider",
        one_of=[
            SEARCH_FILTER_DATETIME,
            SEARCH_FILTER_CQL2,
            SEARCH_FILTER_SPATIAL,
            SEARCH_TRANSFORM_RENAME_FIELDS,
            SEARCH_TRANSFORM_COMBINE_FIELDS,
            PIXELS_TRANSFORM_COLORMAP,
            PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS,
        ],
    )
    properties = _DictDescr(doc="properties (if any) to configure the middleware")


class SearchFilter(_Middleware):
    @staticmethod
    def cql2_filter() -> "SearchFilter":
        return SearchFilter(type=SEARCH_FILTER_CQL2)

    @staticmethod
    def spatial() -> "SearchFilter":
        return SearchFilter(type=SEARCH_FILTER_SPATIAL)

    @staticmethod
    def datetime(field: str) -> "SearchFilter":
        return SearchFilter(type=SEARCH_FILTER_DATETIME, properties={"datetime_field": field})


class SearchTransform(_Middleware):
    @staticmethod
    def rename_fields(case=None, field_map={}) -> "SearchTransform":
        """rename fields in the `properties` of a search response

        Args:
            case (str, optional): case to apply to the field names. Defaults to None. One of ["upper", "lower"]
            field_map (dict, optional): mapping of old field names to new field names. Defaults to {}.
        """
        properties = {"field_map": field_map}
        if case is not None and case in ["upper", "lower"]:
            properties["case"] = case
        elif case is not None:
            raise ValueError(f"case must be one of ['upper', 'lower'], got {case}")

        return SearchTransform(type=SEARCH_TRANSFORM_RENAME_FIELDS, properties=properties)

    @staticmethod
    def combine_fields(
        new_field: str, fields: List[str], separator: str = "", sprintf: str = ""
    ) -> "SearchTransform":
        """combine fields in the `properties` of a search response

        Args:
            new_field (str): name of the new field to create
            fields (List[str]): fields to combine
            separator (str, optional): separator to use when combining fields. Defaults to " ".
            sprintf (str, optional): sprintf format to use when combining fields. This uses golang
            format strings to format the fields into one combined string field. For instance,
            "%d.2 %s" would print "2.00 dollars" if the field values were 2 and "dollars".
            For more information about the formatting see https://pkg.go.dev/fmt.
            All fields must have values for the sprintf to be executed. Defaults to "".
        """
        return SearchTransform(
            type="combine-fields",
            properties={
                "new_field": new_field,
                "fields": fields,
                "separator": separator,
                "sprintf": sprintf,
            },
        )


class PixelsTransform(_Middleware):
    @staticmethod
    def colormap(
        *,
        asset: str,
        band: Union[int, str],
        colormap_name: str = "magma",
        lookup_table: List[List[int]] = None,
        min: float = None,
        max: float = None,
        rescale: bool = False,
        no_data_value: float = None,
    ) -> "PixelsTransform":
        properties = {
            "asset": asset,
            "band": band,
            "colormap_name": colormap_name,
            "rescale": rescale,
        }
        if lookup_table is not None:
            properties.pop("colormap_name")
            properties["lookup_table"] = lookup_table
        if min is not None:
            properties["min"] = min
        if max is not None:
            properties["max"] = max
        if no_data_value is not None:
            properties["no_data_value"] = no_data_value

        return PixelsTransform(type=PIXELS_TRANSFORM_COLORMAP, properties=properties)

    @staticmethod
    def default_asset_bands(default_asset_bands: List[AssetBands]) -> "PixelsTransform":
        return PixelsTransform(
            type=PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS,
            properties={"asset_bands": default_asset_bands},
        )


class MiddlewareConfig(_APIObject):
    search_filters = _ListDescr(
        item_type=(SearchFilter, dict),
        coerce_items=True,
        doc="Which filter actions to perform applied to the result of a dataset.",
    )
    search_transforms_before = _ListDescr(
        item_type=(SearchTransform, dict),
        coerce_items=True,
        doc="transforms to be applied to each feature/item in a search response. "
        "This is applied BEFORE any filtering takes place",
    )
    search_transforms_after = _ListDescr(
        item_type=(SearchTransform, dict),
        coerce_items=True,
        doc="transforms to be applied to each feature/item in a search response. "
        "This is applied AFTER any filtering takes place",
    )
    pixels_transforms = _ListDescr(
        item_type=(PixelsTransform, dict),
        coerce_items=True,
        doc="transforms the request/response of a pixels handler. Useful for "
        "things like applying colormaps or more complex transformations on the pixels data.",
    )
