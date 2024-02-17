from buz.event.kombu import KombuConsumer
from buz.event.kombu.execution_strategy.execution_strategy import ExecutionStrategy


class SelfProcessExecutionStrategy(ExecutionStrategy):
    def __init__(self, kombu_consumer: KombuConsumer):
        self.__kombu_consumer = kombu_consumer

    def start(self) -> None:
        self.__kombu_consumer.run()

    def stop(self) -> None:
        self.__kombu_consumer.should_stop = True
