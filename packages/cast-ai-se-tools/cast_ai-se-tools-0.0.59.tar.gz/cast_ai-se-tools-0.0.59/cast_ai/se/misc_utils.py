import logging
import platform
import shutil


from cast_ai.se.constants import (LINUX_GET_DEPLOYMENTS_CMD, LINUX_GET_NONZERO_DEPLOYMENTS_CMD,
                                  WIN_GET_NONZERO_DEPLOYMENTS_CMD, WIN_GET_DEPLOYMENTS_CMD, REQUIRED_TOOLS)


def get_get_deployments_command(kill_deployments: bool = False) -> str:
    os_system = platform.system()
    logger = logging.getLogger(__name__)
    if os_system == "Windows":
        logger.debug("Running on Windows...")
        if kill_deployments:
            return WIN_GET_NONZERO_DEPLOYMENTS_CMD
        return WIN_GET_DEPLOYMENTS_CMD

    elif os_system == "Linux":
        logger.debug("Running on Linux...")
        if kill_deployments:
            return LINUX_GET_NONZERO_DEPLOYMENTS_CMD
        return LINUX_GET_DEPLOYMENTS_CMD
    else:
        logger.debug(f"Unsupported OS={os_system}")
        raise RuntimeError(f"Unsupported OS={os_system}")


def validate_kctl_required_tools_exist() -> None:
    logger = logging.getLogger(__name__)
    for tool in REQUIRED_TOOLS:
        if not shutil.which(tool):
            logger.critical(f"{tool} was not found (possibly not in PATH)")
            raise RuntimeError(f"{tool} was not found (possibly not in PATH)")
