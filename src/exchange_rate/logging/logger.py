import logging

from rich.console import Console
from rich.logging import RichHandler

from exchange_rate.config import config
from exchange_rate.logging.singleton import SingletonMeta


class AppLogger(metaclass=SingletonMeta):
    """This class provides a logger that follows the Singleton pattern."""

    _logger: logging.Logger

    def __init__(self):
        """Initialize the logger."""
        self._logger = logging.getLogger("app_logger")  # Changed the logger name
        self._logger.setLevel(logging.DEBUG)  # Set the desired logging level
        self._logger.propagate = False
        # Ensure the logger has no other handlers
        if not self._logger.hasHandlers():
            if config.ENVIRONMENT == "local":
                # Use RichHandler only in local environment
                rich_handler = RichConsoleHandler()
                rich_handler.setFormatter(
                    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
                )
                self._logger.addHandler(rich_handler)
            else:
                # Use standard StreamHandler for non-local environments
                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(
                    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
                )
                self._logger.addHandler(stream_handler)

    def get_logger(self):
        """Return the logger instance."""
        return self._logger

    @staticmethod
    def get_instance():
        """Return the singleton instance of the AppLogger class."""
        return AppLogger()


class RichConsoleHandler(RichHandler):
    """Custom RichHandler for console output."""

    def __init__(self, width=200, style=None, **kwargs):
        """Initialize the RichConsoleHandler."""
        super().__init__(
            console=Console(color_system="256", width=width, style=style), **kwargs
        )
