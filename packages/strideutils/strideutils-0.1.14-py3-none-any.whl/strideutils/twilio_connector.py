from typing import Iterable, List, Union

from twilio.rest import Client

from strideutils.stride_config import config

# Check for necessary config on import
_ = config.TWILIO_ALERTS_NUMBER
CALL_TEMPLATE = """<Response><Say>{}</Say></Response>"""

client = Client(config.TWILIO_ACCOUNT_ID, config.TWILIO_API_TOKEN)


# N.B. SMS not available without opt-in logic for apps for toll-free verification


def send_calls(msg: str, to: Union[str, Iterable[str], List[str]]) -> None:
    """
    Make a phone call

    Args:
        msg: A timl formatted message to read aloud to the recipient
        to: A name or list of names that can be looked up in config.PHONE_NUMBERS
        mapping to a 11 digit phone number, with international prefix
        e.g. config.PHONE_NUMBERS['joe'] = +12223334545
    """
    to = [to] if type(to) is str else to
    voice_message = CALL_TEMPLATE.format(msg)
    for destination in to:
        number = config.PHONE_NUMBERS[destination]
        client.calls.create(to=number, from_=config.TWILIO_ALERTS_NUMBER, twiml=voice_message)
