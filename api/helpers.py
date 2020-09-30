import math

from connexion import request
from flask import jsonify


def get(model, query_id):
    return jsonify(model.query.get(query_id).serialize())


def search(model, page, limit):
    count = model.query.count()
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
                    model.query.limit(limit).offset((page - 1) * limit).all(),
                )
            ),
        }
    )
