import datetime
import typing

from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from google.cloud.spanner_v1 import param_types, Type, JsonObject
from google.cloud.spanner_v1.streamed import StreamedResultSet


def zip_results(result_set: StreamedResultSet, field_names: typing.List[str] = None):
    """
    :param result_set: the results
    :param field_names: list of field names. If none is provided, then we use the column names.
    :return: a list of dict(s) zipped with {field_name/column_name: column_value}
    """
    _results = []
    for row in result_set:
        if field_names is None:
            field_names = [field.name for field in result_set.fields]
        _results.append(dict(zip(field_names, row)))
    return _results


def zip_first_result(
    result_set: StreamedResultSet, field_names: typing.List[str] = None
) -> typing.Optional[dict]:
    """
    :param result_set: the results
    :param field_names: list of field names. If none is provided, then we use the column names.
    :return: a single dict zipped with {field_name/column_name: column_value} or None
    """
    for row in result_set:
        if field_names is None:
            field_names = [field.name for field in result_set.fields]
        return dict(zip(field_names, row))
    return None


def single_result(result_set: StreamedResultSet) -> typing.Optional[typing.Any]:
    """
    :param result_set: the results
    :return: the first column value of the first row or None
    """
    for row in result_set:
        return row[0]
    return None


def _sanitize_value(v: typing.Any):
    if isinstance(v, dict):
        return JsonObject(v)
    return v


def _resolve_type(v: typing.Any) -> Type:
    if isinstance(v, int):
        return param_types.INT64
    if isinstance(v, float):
        return param_types.FLOAT64
    if isinstance(v, bool):
        return param_types.BOOL
    if isinstance(v, str):
        return param_types.STRING
    if isinstance(v, (datetime.datetime, DatetimeWithNanoseconds)):
        return param_types.TIMESTAMP
    if isinstance(v, datetime.date):
        return param_types.DATE
    if isinstance(v, dict):
        return param_types.JSON
    if isinstance(v, (list, set, tuple)):
        if not len(v):
            raise ValueError(f"Cannot resolve type of empty list/set/tuple")
        item_type = _resolve_type(v[0])
        return param_types.Array(item_type)
    raise ValueError(f"Unsupported type {type(v)}")


def build_params_ptypes(
    values: dict,
) -> (typing.Dict[str, typing.Any], typing.Dict[str, Type]):
    params = {}
    ptypes = {}
    for k, v in values.items():
        if v is not None:
            params.update({k: _sanitize_value(v)})
            ptypes.update({k: _resolve_type(v)})
    return (
        params,
        ptypes,
    )


def build_params_ptypes_as_kwargs(
    values: dict,
) -> (typing.Dict[str, typing.Any], typing.Dict[str, Type]):
    """
    Utility method to build `params` and `param_types` out of one single dict.
    Example:

        result_set = await snapshot.execute_sql(
            sql="SELECT * FROM Users WHERE user_id = @user_id",
            **build_params_ptypes_as_kwargs({"user_id": user_id}),
        )
    """
    params, ptypes = build_params_ptypes(values)
    return {
        "params": params,
        "param_types": ptypes,
    }
