from flask import current_app


def add_to_index(index, model):
    if not current_app.elasticsearch:  # type:ignore
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(  # type:ignore
        index=index, id=model.id, document=payload
    )


def remove_from_index(index, model):
    if not current_app.elasticsearch:  # type:ignore
        return
    current_app.elasticsearch.delete(index=index, id=model.id)  # type:ignore


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:  # type:ignore
        return [], 0
    search = current_app.elasticsearch.search(  # type:ignore
        index=index,
        query={"multi_match": {"query": query, "fields": ["*"]}},
        from_=(page - 1) * per_page,
        size=per_page,
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]["value"]
