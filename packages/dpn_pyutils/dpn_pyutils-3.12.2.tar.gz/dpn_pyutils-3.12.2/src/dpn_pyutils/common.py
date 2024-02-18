import logging
import logging.config
from pathlib import Path

# This global gets populated when initialize_logging() is called below
# and is used to set the project name for logging namespace below
LOGGING_PROJECT_NAME = ""


class PyUtilsLogger(logging.Logger):
    """
    Overwrites the configured logging class with additional log methods
    """

    TRACE: int = logging.DEBUG - 5

    def trace(self, msg, *args, **kwargs) -> None:
        """
        Enter a log entry at the TRACE level
        """
        self.log(PyUtilsLogger.TRACE, msg, *args, **kwargs)


def initialize_logging(logging_config: dict) -> None:
    """
    Initialises logging for the entire system
    """
    # Add the TRACE level to our log
    logging.addLevelName(PyUtilsLogger.TRACE, "TRACE")
    logging.setLoggerClass(PyUtilsLogger)

    # Check to see if the file path for any file configuration
    # exists and if not, try to create the path
    for handler in logging_config["handlers"]:
        for key in logging_config["handlers"][handler]:
            if key.lower() == "filename":
                file_path = Path(logging_config["handlers"][handler][key])
                if not file_path.parent.exists():
                    file_path.parent.mkdir(parents=True, exist_ok=True)

    if "logging_project_name" in logging_config:
        global LOGGING_PROJECT_NAME
        LOGGING_PROJECT_NAME = logging_config["logging_project_name"]

    logging.config.dictConfig(logging_config)


def get_logger(module_name: str) -> PyUtilsLogger:
    """
    Gets a namespaced logger based on the project name and module name
    """
    if "" == LOGGING_PROJECT_NAME:
        return get_fqn_logger(module_name)

    return get_fqn_logger("{}.{}".format(LOGGING_PROJECT_NAME, module_name))


def get_fqn_logger(module_name: str) -> PyUtilsLogger:
    """
    Gets a namespaced logger based on the fully-qualified name supplied
    """

    if logging.getLoggerClass() != PyUtilsLogger:
        raise RuntimeError(
            "Logging has not been initialised and logging class is not PyUtilsLogger. Please call "
            "initialize_logging() first in order to use this logger."
        )

    return logging.getLogger(module_name)  # type: ignore
