import math
from typing import Any
from typing import cast
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Union

from connexion import request
from flask import jsonify
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.sql.elements import BinaryExpression

from api.db import Base

ColumnName = str  # The column name in the model
Expression = str  # The sql expression to apply on the column
BasicQueryFilterConfig = Tuple[ColumnName, Expression, Any]
QueryFilterConfig = Union[
    BasicQueryFilterConfig, Tuple[Union[and_, or_], Iterable["QueryFilterConfig"]]
]


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


def get(model: Base, query_id: Union[str, int]):
    return jsonify(model.query.get(query_id).serialize())


def search(
    model: Base,
    page: int,
    limit: int,
    query_filters_config: Iterable[QueryFilterConfig] = (),
) -> dict:
    """
    :param model: A SQLAlchemy model
    :param page: The page number in the query result
    :param limit: Number of items per page
    :param query_filters_config: An iterable of filters to apply to the query
           (see `QueryFilterConfig` for the structure of the iterable items)
    """
    query_filters: List[BinaryExpression] = []

    for query_filter_config in query_filters_config:
        query_filters.append(process_query_filters(model, query_filter_config))

    query = model.query.filter(*query_filters)
    count = query.count()
    total_pages = math.ceil(count / limit)

    previous_url = None
    if page > 1:
        previous_url = (
            f"{request.base_url}?page={min(page - 1, total_pages)}&limit={limit}"
        )

    next_url = None
    if page * limit < count:
        next_url = f"{request.base_url}?page={page + 1}&limit={limit}"

    return jsonify(
        {
            "count": count,
            "first": f"{request.base_url}?page=1&limit={limit}",
            "last": f"{request.base_url}?page={total_pages}&limit={limit}",
            "previous": previous_url,
            "next": next_url,
            "results": list(
                map(
                    lambda x: x.serialize(),
                    query.limit(limit).offset((page - 1) * limit).all(),
                )
            ),
        }
    )
