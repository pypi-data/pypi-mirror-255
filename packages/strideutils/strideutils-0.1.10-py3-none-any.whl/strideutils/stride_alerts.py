import datetime
import os
from enum import Enum
from functools import wraps
from typing import Callable, Iterable, List, Optional, Union, cast

import pandas as pd
import tabulate

from strideutils import slack_connector, twilio_connector
from strideutils.stride_config import config


class AlertType(Enum):
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'


def get_tags(individuals: Union[str, Iterable[str]]) -> str:
    """Fetch slack ids for founders"""
    individuals = [individuals] if type(individuals) is str else individuals
    return " ".join(f"<@{config.slack_channels.get(person.lower(), person)}>" for person in individuals)


def df_to_message_body(df: pd.DataFrame) -> str:
    """Helper function to prettify a pandas dataframe for the slack message"""
    table = tabulate.tabulate(df, headers='keys', tablefmt='pretty', showindex=False)  # type: ignore
    return f"```\n{table}\n```"


def notify(
    msgs: Union[str, List[str]],
    urgency,
    tag: Optional[Union[str, Iterable[str]]] = None,
    call: Optional[Union[str, Iterable[str]]] = None,
    beta_alert: bool = False,
    debug_readme_section: str = "",
) -> None:
    """
    Post an alert in the proper channel and optionally call

    Args:
        msgs: A string or list of strings to notify on
        urgency: One of 'debug', 'info', 'warning', or 'critical'
        tag: A single or list of names or slack ids
        beta_alert: Modfies top-level message to not it's a work in progress
    """
    urgency = AlertType(urgency)

    msgs: List = cast(List, [msgs] if type(msgs) is str else msgs)
    top_level_message = str(msgs[0])

    debug_msg = f"Read more: {config.alerts_playbook}{debug_readme_section}"

    channel = "#alerts-info"
    if urgency == AlertType.DEBUG:
        channel = "#alerts-debug"
    elif urgency == AlertType.INFO:
        channel = "#alerts-info"
    elif urgency == AlertType.WARNING:
        channel = "#alerts-warnings"
    elif urgency == AlertType.CRITICAL:
        channel = "#alerts-critical"

    if beta_alert:
        msgs[0] += "\nβ _This alert is in beta and might be unstable_"

    if tag:
        msgs[0] += f"\n{get_tags(tag)}"

    slack_connector.post_msg(msgs + [debug_msg], channel)

    if call:
        twilio_connector.send_calls(top_level_message, call)


def raise_alert(
    urgency: Union[AlertType, str],
    tag: Optional[Union[str, Iterable[str]]] = None,
    call: Optional[Union[str, Iterable[str]]] = None,
    beta_alert: bool = False,
    debug_readme_section: str = "",
) -> Callable:
    """
    Modify an alert to notify users based on severity

    The alert should have a return signature of
    msgs: Union[str, Iterable[str]]

    For local testing, set an environment variable ENV=DEV or use
    urgency='debug'
    """
    urgency = AlertType(urgency)
    if urgency == AlertType.DEBUG or os.environ.get('ENV') == 'DEV':
        call, tag = [], []
        urgency = AlertType.DEBUG

    def _decorator(f: Callable):
        @wraps(f)
        def _func(*args, **kwargs):
            msgs = f(*args, **kwargs)
            if urgency == 'debug':
                debug_msg = (
                    'In debug mode. Tags and calls have been disabled' 'and the message is routed to alerts-debug.'
                )
                print(debug_msg)
                msgs += [debug_msg]
            if msgs:
                notify(
                    msgs=msgs,
                    urgency=urgency,
                    tag=tag,
                    call=call,
                    beta_alert=beta_alert,
                    debug_readme_section=debug_readme_section,
                )

        return _func

    return _decorator


def run_daily(utc_hour_or_alert: Union[int, Callable]) -> Callable:
    """
    Modifies an function to only run when the utc_hour matches the current time
    E.g. run_daily(5) would run if it's 5-6 UTC

    Runs at noon est by default, but can be modified:
    ```
    # Run if it's 17:00 utc
    @run_daily
    def foo():
        ...

    # Run if its 2:00 utc
    @run_daily(2)
    def bar():
        ...
    ```
    """
    DEFAULT_UTC_HOUR = 17

    # If used without an argument, act as an unparameterized decorator
    if callable(utc_hour_or_alert):
        alert = utc_hour_or_alert

        @wraps(alert)
        def _func(*args, **kwargs):
            dt = datetime.datetime.utcnow()
            if dt.hour == DEFAULT_UTC_HOUR:
                return alert(*args, **kwargs)

        return _func

    # Otherwise return a decorator which modifies the function based on the
    # parameter
    assert type(utc_hour_or_alert) is int
    utc_hour = utc_hour_or_alert

    def _decorator(f: Callable):
        @wraps(f)
        def _func(*args, **kwargs):
            dt = datetime.datetime.utcnow()
            if dt.hour == utc_hour:
                return f(*args, **kwargs)

        return _func

    return _decorator


def run_epochly(f: Callable) -> Callable:
    """
    Modifies an function to run once per stride epoch
    """

    @wraps(f)
    def _func(*args, **kwargs):
        dt = datetime.datetime.utcnow()
        if dt.hour in {1, 7, 13, 19}:
            return f(*args, **kwargs)

    return _func
