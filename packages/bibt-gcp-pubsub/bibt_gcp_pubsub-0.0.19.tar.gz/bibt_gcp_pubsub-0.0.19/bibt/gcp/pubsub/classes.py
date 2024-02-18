import json
import logging

import google.auth.transport.requests
from google.cloud import pubsub_v1

_LOGGER = logging.getLogger(__name__)


class Client:
    """A Client may be used to interact with the GCP PubSub API using the
        same session / credentials.

    :type credentials: ``google.oauth2.credentials.Credentials``
    :param credentials: the credentials object to use when making the API call, if
        not to use the inferred gcloud account.
    """

    def __init__(self, credentials=None):
        self._client = pubsub_v1.PublisherClient(credentials=credentials)

    def _ensure_valid_client(self):
        try:
            credentials = self._client._credentials
        except AttributeError:
            try:
                credentials = self._client._transport._credentials
            except AttributeError:
                logging.error("Could not verify credentials in client.")
                return
        if not credentials.valid or not credentials.expiry:
            logging.info(
                "Refreshing client credentials, token expired: "
                f"[{str(credentials.expiry)}]"
            )
            request = google.auth.transport.requests.Request()
            credentials.refresh(request=request)
            logging.info(f"New expiration: [{str(credentials.expiry)}]")
        else:
            logging.debug(
                f"Token is valid: [{credentials.valid}] "
                f"expires: [{str(credentials.expiry)}]"
            )
        return

    def send_pubsub(self, topic_uri, payload):
        """
        Publishes a pubsub message to the specified topic. Executing account
        must have pubsub publisher permissions on the topic or in the project.

        .. code:: python

            from bibt.gcp.pubsub import Client
            def main(event, context):
                client = Client()
                topic_uri = (
                    f'projects/{os.environ["GOOGLE_PROJECT"]}'
                    f'/topics/{os.environ["NEXT_TOPIC"]}'
                )
                client.send_pubsub(
                    topic_uri=topic_uri,
                    payload={'favorite_color': 'blue'}
                )

        :type topic_uri: :py:class:`str`
        :param topic_uri: the topic on which to publish.
            topic uri format: ``'projects/{project_name}/topics/{topic_name}'``

        :type payload: :py:class:`dict` :py:class:`list` OR :py:class:`str`
        :param payload: the pubsub payload. can be a ``dict``, ``list``, or ``str``.
            will be converted to bytes before sending.
        """
        _LOGGER.info(f"Sending pubsub to topic: [{topic_uri}]")
        _LOGGER.debug(f"Payload: {payload}")
        # Convert to Bytes then publish message.
        if isinstance(payload, dict) or isinstance(payload, list):
            payload = json.dumps(payload, default=str)
        payload_bytes = payload.encode("utf-8")
        self._ensure_valid_client()
        future = self._client.publish(topic=topic_uri, data=payload_bytes)
        msg_id = future.result()
        _LOGGER.info(f"PubSub sent successfully, pubsub message ID: [{msg_id}]")
        return msg_id
