from dataclasses import asdict
from typing import Collection, List, Optional, Set, Dict

from kombu import Connection, Exchange, Producer
from kombu.entity import PERSISTENT_DELIVERY_MODE

from buz.event import Event, EventBus
from buz.event.kombu import EventNotPublishedException
from buz.event.kombu.publish_strategy import PublishStrategy
from buz.event.kombu.retry import PublishRetryPolicy, SimplePublishRetryPolicy
from buz.event.kombu.serializer_enum import SerializerEnum
from buz.event.middleware import (
    PublishMiddleware,
    PublishMiddlewareChainResolver,
)


class KombuEventBus(EventBus):
    def __init__(
        self,
        connection: Connection,
        publish_strategy: PublishStrategy,
        publish_retry_policy: PublishRetryPolicy = SimplePublishRetryPolicy(),
        serializer: Optional[SerializerEnum] = SerializerEnum.JSON,
        publish_middlewares: Optional[List[PublishMiddleware]] = None,
    ):
        self.__connection = connection
        self.__publish_strategy = publish_strategy
        self.__publish_retry_policy = publish_retry_policy
        self.__serializer = serializer
        self.__publish_middleware_chain_resolver = PublishMiddlewareChainResolver(publish_middlewares or [])
        self.__declared_exchanges: Set[Exchange] = set()
        self.__producer: Optional[Producer] = None

    def publish(self, event: Event) -> None:
        self.__publish_middleware_chain_resolver.resolve(event, self.__perform_publish)

    def __perform_publish(self, event: Event) -> None:
        try:
            event_fqn = event.fqn()
            exchange = self.__get_exchange(event_fqn)
            routing_key = self.__publish_strategy.get_routing_key(event_fqn)

            producer = self.__get_producer()

            body = self.__get_body(event)
            headers = self.__get_headers(event)

            producer.publish(
                body,
                exchange=exchange,
                routing_key=routing_key,
                retry=True,
                retry_policy=self.__publish_retry_policy.to_kombu_retry_policy(event),
                headers=headers,
                delivery_mode=PERSISTENT_DELIVERY_MODE,
            )
        except Exception as exc:
            raise EventNotPublishedException(event) from exc

    def __get_exchange(self, event_fqn: str) -> Exchange:
        exchange = self.__publish_strategy.get_exchange(event_fqn)

        if exchange not in self.__declared_exchanges:
            self.__declare_exchange(exchange)

        return exchange

    def __declare_exchange(self, exchange: Exchange) -> None:
        auto_retry_declare = self.__connection.autoretry(exchange.declare)
        auto_retry_declare()
        self.__declared_exchanges.add(exchange)

    def __get_producer(self) -> Producer:
        if self.__producer is None:
            self.__producer = self.__connection.Producer(serializer=self.__serializer)

        return self.__producer

    def __get_body(self, event: Event) -> Dict:
        return asdict(event)

    def __get_headers(self, event: Event) -> Dict:
        return {"fqn": event.fqn()}

    def bulk_publish(self, events: Collection[Event]) -> None:
        for event in events:
            self.publish(event)
