from contextlib import ExitStack, contextmanager

from uhura.base import Readable, Writable
from uhura.caches import (
    CachingService,
)
from uhura.caching import (
    cache_local_input,
    compare_known_good_output,
    replace_local_input,
    save_known_good_output,
)
from uhura.properties.property_tester import PropertyTester
from uhura.properties.transformer import Transformer

try:
    from uhura.pandas_tools import pandas_comparator as default_comparator
    from uhura.properties.testable_properties import DEFAULT_PROPERTIES
except ImportError:
    from uhura.caches import basic_comparator as default_comparator

    DEFAULT_PROPERTIES = tuple()


@contextmanager
def _compose_contexts(*contexts):
    with ExitStack() as stack:
        for context in contexts:
            stack.enter_context(context)
        yield


def fixture_builder_mode(
    *,
    known_good_path: str = "tests/fixtures/output_known_good",
    input_path: str = "tests/fixtures/input",
    stream_cache_depth: int = 3,
):
    return _compose_contexts(
        Readable.decorated_with(
            cache_local_input(
                CachingService.default(base_path=input_path, depth=stream_cache_depth)
            )
        ),
        Writable.decorated_with(
            save_known_good_output(CachingService.default(base_path=known_good_path))
        ),
    )


def task_test_mode(
    *,
    known_good_path: str = "tests/fixtures/output_known_good",
    input_path: str = "tests/fixtures/input",
    comparison=default_comparator,
):
    return _compose_contexts(
        Readable.decorated_with(replace_local_input(CachingService.default(base_path=input_path))),
        Writable.decorated_with(
            compare_known_good_output(
                CachingService.default(base_path=known_good_path), comparison=comparison
            )
        ),
    )


_tester = PropertyTester.create_for_properties(DEFAULT_PROPERTIES)


@contextmanager
def test_transformers(tester=_tester):
    """
    The test_transformers mode activates property testing for all functions annotated as 'transformers'.

    To use specific tests, or a specific testing mechanism, use the optional 'tester' argument to provide an
    alternative.
    """
    Transformer.tester = tester
    try:
        yield
    finally:
        Transformer.tester = None
