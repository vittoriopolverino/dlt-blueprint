import logging
from dataclasses import dataclass, field
from typing import Dict


class Singleton(type):
    _instances: Dict[type, 'Singleton'] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass(frozen=True)
class Logger(metaclass=Singleton):
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger(__name__))
