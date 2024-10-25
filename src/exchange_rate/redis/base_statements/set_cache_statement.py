from abc import ABC, abstractmethod


class SetCacheStatement(ABC):
    """Abstract class for setting cache key and value."""

    def __init__(self, values):
        self.values = values
        self.name = ""
        self._time_to_live = 30  # default TTL in seconds

    @property
    @abstractmethod
    def cache_key(self) -> str:
        """Abstract property to return the cache key."""

    @property
    @abstractmethod
    def cache_value(self) -> dict:
        """Abstract property to return the cache value."""

    @property
    def time_to_live(self) -> int:
        """Property to return the time-to-live for the cache."""
        return self._time_to_live
