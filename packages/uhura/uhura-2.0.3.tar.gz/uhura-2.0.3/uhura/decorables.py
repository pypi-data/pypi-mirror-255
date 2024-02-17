from contextlib import contextmanager


def get_original(method):
    return getattr(method, "__wrapped__", method)


def is_wrapper(attr):
    return hasattr(attr, "__wrapped__")


class Decorable:
    _decorators = []

    @classmethod
    def _apply_to_current_subclasses(cls, decorator):
        for subclass in cls.__subclasses__():
            decorator(subclass)

    def __init_subclass__(cls, **kwargs):
        cls._decorators = cls._decorators.copy()
        for decorator in cls._decorators:
            decorator(cls)
        super().__init_subclass__(**kwargs)
        pass

    @classmethod
    def add_decorator(cls, decorator):
        cls._apply_to_current_subclasses(decorator)
        cls._decorators.append(decorator)

    @classmethod
    def remove_last_decorator(cls):
        def _revert_decoration(child_cls):
            for key, attr in vars(child_cls).items():
                if is_wrapper(attr) and hasattr(cls, key):
                    setattr(child_cls, key, get_original(attr))

        cls._apply_to_current_subclasses(_revert_decoration)
        cls._decorators.pop()

    @classmethod
    @contextmanager
    def decorated_with(cls, decorator):
        try:
            cls.add_decorator(decorator)
            yield
        finally:
            cls.remove_last_decorator()
