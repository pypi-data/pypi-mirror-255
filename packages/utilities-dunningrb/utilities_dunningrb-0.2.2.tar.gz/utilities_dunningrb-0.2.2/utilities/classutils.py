"""Defines the Singleton and UniqueInstance metaclasses.
"""
import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)


class Singleton(type):
    """A standard singleton metaclass. Only one instance of a Singleton can be instantiated at
    runtime. If a request is made to instantiate a new Singleton, the existing Singleton is
    returned.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls.__name__ not in cls._instances.keys():
            cls._instances[cls.__name__] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls.__name__]

    @classmethod
    def get_instances(mcs):
        return mcs._instances


class UniqueInstance(type):
    """A metaclass to provide instances with a unique identifier if no existing instance has
    that same identifier (otherwise return that instance).
    """

    _instances = {}

    def __call__(cls: Any, *args: Any, **kwargs: Any) -> Any:
        """Implements a factory pattern to return a new instance if there is no existing instance
        with the same ID; otherwise returns the existing instance with that ID. Skips __init__
        methods in all derived classes if returning an existing instance.
        """
        params = [i for i in list(args) + list(kwargs.values())]
        param_str = ".".join([str(i) for i in params])
        param_hex = hashlib.md5(param_str.encode()).hexdigest()

        cls._id = f"{cls.__name__}:{param_hex}"

        if cls._id not in cls._instances:
            self = cls.__new__(cls, *args, **kwargs)
            cls._instances[cls._id] = self
            cls.__init__(self, *args, **kwargs)

        return cls._instances[cls._id]

    def __init__(cls, *args, **kwargs):
        """Initialize the child class instance if returning a new instance."""
        super(UniqueInstance, cls).__init__(*args, **kwargs)

    @classmethod
    def get_instances(mcs):
        return mcs._instances
