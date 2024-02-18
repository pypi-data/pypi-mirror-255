from rekuest.actors.vars import (
    get_current_assignation_helper,
    get_current_provision_helper,
)
from rekuest.api.schema import LogLevelInput


async def alog(message: str, level: LogLevelInput = LogLevelInput.DEBUG) -> None:
    await get_current_assignation_helper().alog(level, message)


def log(message: str, level: LogLevelInput = LogLevelInput.DEBUG) -> None:
    get_current_assignation_helper().log(level, message)


async def plog(message: str, level: LogLevelInput = LogLevelInput.DEBUG) -> None:
    await get_current_provision_helper().alog(level, message)


def useUser() -> str:
    """Returns the user id of the current assignation"""
    return get_current_assignation_helper().user


def useGuardian() -> str:
    """Returns the guardian id of the current provision"""
    return get_current_provision_helper().guardian


def useInstanceID() -> str:
    """Returns the guardian id of the current provision"""
    return get_current_assignation_helper().passport.instance_id


def progress(percentage: int) -> None:
    """Progress

    Args:
        percentage (int): Percentage to progress to
    """

    helper = get_current_assignation_helper()
    helper.progress(percentage)


async def aprogress(percentage: int) -> None:
    """Progress

    Args:
        percentage (int): Percentage to progress to
    """

    helper = get_current_assignation_helper()
    await helper.aprogress(percentage)
