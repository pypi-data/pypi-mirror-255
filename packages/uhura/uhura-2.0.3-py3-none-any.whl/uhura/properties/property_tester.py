import logging
from abc import ABCMeta, abstractmethod
from typing import NamedTuple, Optional, Callable, TypeVar, Tuple, Collection
from collections import defaultdict
from contextlib import contextmanager
from graphlib import TopologicalSorter


ARG = TypeVar("ARG")
PropertyTest = Callable[[Callable[[ARG], ARG], ARG], Tuple[ARG, bool]]
UHURA_PROPERTIES_LOGGER_NAME = "uhura.properties"
logger = logging.getLogger(UHURA_PROPERTIES_LOGGER_NAME)
logger.setLevel(logging.INFO)


SENTINEL = object()  # unique object used to signal we have never ran `tested`


@contextmanager
def set_loggers_to_error_only():
    """Testing properties may lead to call the same function multiple
    times and also call all the other functions the tested one will call.
    Obviously we can to limit the number of unnecessary calls,
    but we won't be able to ensure we do only one call per function. So,
    we want to suppress the logs for all the extra calls we do.

    Also, we want to keep on showing error logs in case we have some
    unexpected issues while testing a property that the property itself
    is not accounting for. This should make it easier to debug properties
    """
    loggers = {
        name: logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name != UHURA_PROPERTIES_LOGGER_NAME
    }

    logging_levels = {}
    for name, logger in loggers.items():
        logging_levels[name] = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)
    root_logger_level = logging.getLogger().getEffectiveLevel()
    logging.getLogger().setLevel(logging.ERROR)

    try:
        yield logging_levels
    finally:
        for name, level in logging_levels.items():
            logging.getLogger(name).setLevel(level)
            logging.getLogger().setLevel(root_logger_level)


class PropertyTestResult(NamedTuple):
    prop: Callable
    has_property: bool
    tested_callable_name: str
    notes: Optional[str] = None

    @property
    def property_name(self):
        return self.prop.__qualname__

    def write_to_info(self):
        respected = "has property" if self.has_property else "lacks property"
        base_message = f"[{self.tested_callable_name}]: {respected} {self.property_name}"
        logging.getLogger(UHURA_PROPERTIES_LOGGER_NAME).info(
            base_message if self.notes is None else f"{base_message} - {self.notes}"
        )
        pass


class HierarchicalPropertyRepository:
    def __init__(self, property_graph: TopologicalSorter):
        self._property_graph = property_graph
        self._results = dict()
        self._valid_properties = set()

    def add_result(self, result: PropertyTestResult):
        if result.has_property:
            self._valid_properties.add(result.property_name)
        self._property_graph.done(result.prop)
        self._results[result.property_name] = result
        pass

    def get_properties_to_test(self) -> PropertyTest:
        while self._property_graph.is_active():
            for property_ in self._property_graph.get_ready():
                if all(
                    dependency.__qualname__ in self._valid_properties
                    for dependency in getattr(property_, "depends_on", set())
                ):
                    yield property_
                else:
                    self._property_graph.done(property_)

    @property
    def positive_properties(self):
        return frozenset(self._valid_properties)

    @property
    def results(self):
        return self._results

    @classmethod
    def create_for_properties(cls, properties: Collection[PropertyTest]):
        graph = {prop: getattr(prop, "depends_on", set()) for prop in properties}
        sorter = TopologicalSorter(graph)
        sorter.prepare()
        return cls(sorter)


class VerbosePropertyRepository(HierarchicalPropertyRepository):
    def add_result(self, result: PropertyTestResult):
        result.write_to_info()
        super().add_result(result)


class AbstractPropertyTester(metaclass=ABCMeta):
    @abstractmethod
    def add_properties_to_function(self, tested):
        pass


class PropertyTester(AbstractPropertyTester):
    def __init__(self, repository: defaultdict):
        self._repository = repository

    def get_repository(self, tested) -> HierarchicalPropertyRepository:
        return self._repository[tested.__qualname__]

    def get_results(self, tested, summary=True):
        name = tested.__qualname__
        if name not in self._repository:
            raise KeyError(f"{name} not in tested transformers {self._repository.keys()}")
        if summary:
            return self.get_repository(tested).positive_properties
        return self.get_repository(tested).results

    def add_properties_to_function(self, tested):
        test_repo = self._repository[tested.__qualname__]

        def wrapped(arg):
            result = SENTINEL

            for test in test_repo.get_properties_to_test():
                if test.__qualname__ not in self.get_repository(tested).results:
                    if len(test_repo._results) > 0:
                        with set_loggers_to_error_only():
                            result, *payload = test(tested, arg, result=result)
                    else:
                        result, *payload = test(tested, arg, result=result)
                    if len(payload) == 2:
                        has_prop, notes = payload
                    else:
                        has_prop = payload[0]
                        notes = None
                    test_repo.add_result(
                        PropertyTestResult(
                            prop=test,
                            has_property=has_prop,
                            tested_callable_name=tested.__qualname__,
                            notes=notes,
                        )
                    )
            if result is SENTINEL:
                return tested(arg)
            else:
                return result

        return wrapped

    @classmethod
    def create_for_properties(cls, properties: Collection[PropertyTest]):
        return cls(
            defaultdict(lambda: VerbosePropertyRepository.create_for_properties(properties))
        )


def depends(*on):
    if len(on) == 0:
        raise ValueError("@depends(on=[..]) or @depends(on=prop) is the required call")

    def inner(f):
        setattr(f, "depends_on", getattr(f, "depends_on", set()) | set(on))
        return f

    return inner
