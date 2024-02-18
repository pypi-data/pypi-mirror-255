import base64
import logging
from datetime import datetime
from datetime import timezone

from cloudevents.http import CloudEvent
from dateutil.parser import parse
from google.cloud import functions

_LOGGER = logging.getLogger(__name__)


def process_event(
    event: CloudEvent,
    timeout_secs=600,
    decode_bytes=True,
):
    """Check timestamp of triggering CloudEvent; catches infinite retry
        loops on 'retry on fail' cloud functions. Its good practice to always call
        this function first in a Cloud Function. Additionally, **be sure to wrap
        the call to this function in a try/except block where the except block
        returns normally.** This ensures that an exception raised here does not
        result in an infinite rety loop.

        **If (and only if)** the event has a payload, it will be returned.
        Otherwise, this function returns ``None``.

    .. code-block:: python

        import json
        from bibt.gcp.pubsub import process_event
        from cloudevents.http import CloudEvent
        import functions_framework

        @functions_framework.event
        def main(event: CloudEvent):
            try:
                payload = process_event(event)
                if not payload:
                    raise IOError('No payload in triggering pubsub!')
                payload = json.loads(payload)
            except Exception as e:
                _LOGGER.critical(
                    f'Exception while processing trigger: {type(e).__name__}: {e}'
                )
                return

    :type context: :class:`google.cloud.functions.Context`
    :param context: the triggering pubsub's context.

    :type event: :py:class:`dict`
    :param event: (Optional) the triggering pubsub's event.
        defaults to :py:class:`None`.

    :type timeout_secs: :py:class:`int`
    :param timeout_secs: (Optional) the number of seconds to consider as
        the timeout threshold from the original trigger time. Defaults to 1800.

    :type decode_bytes: :py:class:`bool`
    :param decode_bytes: (Optional) whether to attempt to decode
        the bytes in the event payload as "utf-8" or simply return the bytes.

    :rtype: :py:class:`str` OR :py:class:`bytes` OR :py:class:`None`
    :returns: the pubsub payload, if present.
    """
    _LOGGER.info(f"Processing CloudEvent: {event.id}")
    utctime = datetime.now(timezone.utc)
    eventtime = parse(event.time)
    _LOGGER.debug(f"PubSub timestamp: [{eventtime}]")
    lapsed = utctime - eventtime
    lapsed = lapsed.total_seconds()
    _LOGGER.info(f"Lapsed time since triggering event: {lapsed:.5f} seconds")
    if lapsed > timeout_secs:
        raise TimeoutError(
            f"Threshold of {timeout_secs} seconds exceeded by "
            f"{lapsed-timeout_secs} seconds. Exiting."
        )

    if event.data and "message" in event.data and "data" in event.data["message"]:
        _LOGGER.debug("Payload found, extracting & returning.")
        payload = base64.b64decode(event.data["message"]["data"])
        if decode_bytes:
            _LOGGER.debug("Decoding as UTF-8 and returning a string...")
            return payload.decode("utf-8")
        _LOGGER.debug("Returning as raw bytes...")
        return payload

    return None


def process_trigger(
    context: functions.Context,
    event=None,
    timeout_secs=600,
    decode_bytes=True,
):
    """Check timestamp of triggering event; catches infinite retry
        loops on 'retry on fail' cloud functions. Its good practice to always call
        this function first in a Cloud Function. Additionally, **be sure to wrap
        the call to this function in a try/except block where the except block
        returns normally.** This ensures that an exception raised here does not
        result in an infinite rety loop.

        **If (and only if)** the triggering pubsub's event is also passed **and
        has a payload**, it will be returned. Otherwise, this function returns ``None``.

    .. code-block:: python

        import json
        from bibt.gcp.pubsub import process_trigger
        def main(event, context):
            try:
                payload = process_trigger(context, event=event)
                if not payload:
                    raise IOError('No payload in triggering pubsub!')
                payload = json.loads(payload)
            except Exception as e:
                _LOGGER.critical(
                    f'Exception while processing trigger: {type(e).__name__}: {e}'
                )
                return

    :type context: :class:`google.cloud.functions.Context`
    :param context: the triggering pubsub's context.

    :type event: :py:class:`dict`
    :param event: (Optional) the triggering pubsub's event.
        defaults to :py:class:`None`.

    :type timeout_secs: :py:class:`int`
    :param timeout_secs: (Optional) the number of seconds to consider as
        the timeout threshold from the original trigger time. Defaults to 1800.

    :type decode_bytes: :py:class:`bool`
    :param decode_bytes: (Optional) whether to attempt to decode
        the bytes in the event payload as "utf-8" or simply return the bytes.

    :rtype: :py:class:`str` OR :py:class:`bytes` OR :py:class:`None`
    :returns: the pubsub payload, if present.
    """
    _LOGGER.info(f"Processing PubSub: {context.event_id}")
    utctime = datetime.now(timezone.utc)
    eventtime = parse(context.timestamp)
    _LOGGER.debug(f"PubSub timestamp: [{eventtime}]")
    lapsed = utctime - eventtime
    lapsed = datetime.now(timezone.utc) - parse(context.timestamp)
    lapsed = lapsed.total_seconds()
    _LOGGER.info(f"Lapsed time since triggering event: {lapsed:.5f} seconds")
    if lapsed > timeout_secs:
        raise TimeoutError(
            f"Threshold of {timeout_secs} seconds exceeded by "
            f"{lapsed-timeout_secs} seconds. Exiting."
        )

    if event is not None and "data" in event:
        _LOGGER.debug("Payload found, extracting & returning.")
        payload = base64.b64decode(event["data"])
        if decode_bytes:
            _LOGGER.debug("Decoding as UTF-8 and returning a string...")
            return payload.decode("utf-8")
        _LOGGER.debug("Returning as raw bytes...")
        return payload

    return None
