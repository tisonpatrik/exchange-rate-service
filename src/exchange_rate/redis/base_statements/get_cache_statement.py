from abc import ABC, abstractmethod


class GetCacheStatement(ABC):
    """Abstract class for encapsulating data fetching key for Redis.
    This class must be extended with specific implementations that format or validate queries."""

    def __init__(self, parameter: str):
        self.parameter = parameter

    @property
    @abstractmethod
    def cache_key(self) -> str:
        """Abstract property to return the cache key."""
