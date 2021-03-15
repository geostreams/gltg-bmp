import math
import re
from typing import Any
from typing import cast
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypedDict
from typing import Union

from connexion import request
from sqlalchemy import and_
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import BinaryExpression

from api.db import Base

ColumnName = str  # The column name in the model
Expression = str  # The sql expression to apply on the column
BasicQueryFilterConfig = Tuple[ColumnName, Expression, Any]
QueryFilterConfig = Union[
    BasicQueryFilterConfig, Tuple[Union[and_, or_], Iterable["QueryFilterConfig"]]
]


class SearchResults(TypedDict):
    count: int
    first: str
    last: str
    previous: Optional[str]
    next: Optional[str]
    results: Iterable[Base]


def process_query_filters(
    model: Base, query_filter_config: QueryFilterConfig
) -> BinaryExpression:
    if len(query_filter_config) == 2:
        query_filters = []
        for sub_filter in cast(Iterable[QueryFilterConfig], query_filter_config[1]):
            query_filters.append(process_query_filters(model, sub_filter))
        return query_filter_config[0](*query_filters)
    elif len(query_filter_config) == 3:
        (key, op, value) = cast(BasicQueryFilterConfig, query_filter_config)
        return getattr(getattr(model, key), op)(value)


def get(model: Base, query_id: Union[str, int]) -> Base:
    return model.query.get(query_id)


def search(
    model: Base,
    page: int,
    limit: int,
    query_filters_config: Iterable[QueryFilterConfig] = (),
    columns: Iterable[InstrumentedAttribute] = (),
    group_by: Iterable[str] = (),
    aggregates: Iterable[str] = (),
    partitions: Iterable[str] = (),
    partition_size: int = 0,
    order_by: Iterable[str] = (),
) -> SearchResults:
    """
    :param model: A SQLAlchemy model.
    :param page: The page number in the query result.
    :param limit: Number of items per page.
                  If limit is less than 1, then all the items matching the query will be returned.
    :param query_filters_config: An iterable of filters to apply to the query
           (see `QueryFilterConfig` for the structure of the iterable items).
    :param columns: List of columns to include in the query results. If it's empty, then all columns will be included.
    :param group_by: List of columns to group the query by.
    :param aggregates: List of aggregate function to apply to a column. Each item must be a string in the following
           format: `<column-name>-<aggregate_function>`.
    :param partitions: List of columns to partition over.
    :param partition_size: number of items to include in each partition.
           A non-positive integer means include everything.
    :param order_by: List of columns to order the query by.
           Column names must be prepended with + or -, indicating whether to sort them in ascending or descending
           order respectively.
    :return a dict object in shape of `SearchResult` type.
    """
    query_filters: List[BinaryExpression] = []

    for query_filter_config in query_filters_config:
        query_filters.append(process_query_filters(model, query_filter_config))

    session = model.query.session

    columns = list(columns)
    dynamic_columns = {}

    if group_by:
        columns = columns + list(map(lambda c: getattr(model, c), group_by))

    for aggregate in aggregates:
        (column_name, agg_func) = aggregate.split("-")
        column = getattr(func, agg_func)(getattr(model, column_name))
        columns.append(column.label(aggregate))
        dynamic_columns[aggregate] = column

    if columns:
        query = session.query(*columns)
    else:
        query = session.query(model)

    if group_by:
        query = query.group_by(*group_by)

    order_by_args = []
    if order_by:
        for column_order in order_by:
            if column_order[0] == "-":
                column_name = column_order[1:]
                order_func = desc
            else:
                column_name = column_order
                order_func = asc

            if column_name in dynamic_columns:
                column = dynamic_columns[column_name]
            else:
                column = getattr(model, column_name)

            order_by_args.append(order_func(column))

    query = query.filter(*query_filters)

    if partitions:
        partition_columns = []
        for column_name in partitions:
            if column_name in dynamic_columns:
                partition_columns.append(dynamic_columns[column_name])
            else:
                partition_columns.append(getattr(model, column_name))

        row_number = (
            func.row_number()
            .over(partition_by=partition_columns, order_by=order_by_args)
            .label("row_number")
        )
        query = query.add_column(row_number).from_self()

        if partition_size > 0:
            query = query.filter(row_number <= partition_size)
    else:
        query = query.order_by(*order_by_args)

    count = query.count()

    if limit < 1:
        limit = count

    total_pages = math.ceil(count / limit)

    query_params = re.sub(
        "&$", "", re.sub(r"page=\d+&?", "", request.query_string.decode())
    )

    previous_url = None
    if page > 1:
        previous_url = (
            f"{request.base_url}?page={min(page - 1, total_pages)}&{query_params}"
        )

    next_url = None
    if page * limit < count:
        next_url = f"{request.base_url}?page={page + 1}&{query_params}"

    def query_list_to_dict(items):
        out = {}
        for i, c in enumerate(columns):
            out[c.key] = items[i]
        return out

    results = query.limit(limit).offset((page - 1) * limit).all()
    if columns:
        results = list(map(lambda items: query_list_to_dict(items), results))

    return {
        "count": count,
        "first": f"{request.base_url}?page=1&{query_params}",
        "last": f"{request.base_url}?page={total_pages}&{query_params}",
        "previous": previous_url,
        "next": next_url,
        "results": results,
    }
