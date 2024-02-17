from typing import Type, get_type_hints

from buz.query import Query
from buz.query.asynchronous.query_handler import QueryHandler


class BaseQueryHandler(QueryHandler):
    @classmethod
    def fqn(cls) -> str:
        return f"query_handler.{cls.__module__}.{cls.__name__}"

    @classmethod
    def handles(cls) -> Type[Query]:
        handle_types = get_type_hints(cls.handle)

        if "query" not in handle_types:
            raise TypeError("query parameter not found in handle method")

        if not issubclass(handle_types["query"], Query):
            raise TypeError("query parameter is not an buz.query.Query subclass")

        return handle_types["query"]
