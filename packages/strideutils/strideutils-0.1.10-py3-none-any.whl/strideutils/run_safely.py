import traceback
from typing import Callable, Optional

from strideutils import slack_connector
from strideutils.stride_config import config


def try_and_log_with_status(
    *functions: Callable, slack_channel: str = 'alerts-status', job_name: str = "alerts", botname: Optional[str] = None
):
    """
    Wrap functions in a try/catch and log exceptions.

    If the function failed, an error will get sent to slack_channel.
    If slack_channel is None, no slack message will be sent on failure.

    params
    ------
    functions: Callable
      Driver function
    """
    if config.ENV == 'DEV':
        slack_channel = 'alerts-debug'

    tracebacks = []
    msgs = []
    for func in functions:
        try:
            func()
            msg = [f':white_check_mark: {func.__name__}']
        except Exception:
            msg = [f':x: {func.__name__} ']
            tracebacks.append(f"{func.__name__} \n\n" + traceback.format_exc())
        msgs += msg

    count_succeeded_msg = f"{len(functions) - len(tracebacks)}/{len(functions)} {job_name} succeeded"
    if len(tracebacks) > 0:
        status_msg = f':x: {count_succeeded_msg}'
    else:
        status_msg = f':white_check_mark: {count_succeeded_msg}'

    slack_connector.post_msg([status_msg] + ["\n".join(msgs)] + tracebacks, slack_channel, botname=botname)
