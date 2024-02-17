import logging

log = logging.getLogger(__name__)


class VIBER:

    def __init__(self, client):
        self._client = client

    def send_viber_message(self, recipients: list, content: str, label: str, originator: str, call_back_url: str = None):
        """
        Send a viber message to a single/multiple recipient.
        :param recipients: list - Mobile Numbers to send Viber seperated by comma in an array.
        :param content: str - The message content is being sent.
        :param originator: str - The Sender/Header of a message.
        :param call_back_url: str - receive delivery status.
        :param label: str - Describes the nature of message being sent to end user
        :return:
        """
        message = {
            "channel": "viber",
            "recipients": recipients,
            "content": content,
            "label": label
        }
        message_globals = {
            "originator": originator,
            "call_back_url": call_back_url
        }

        response = self._client.post(self._client.host(), "/viber/v1/send",
                                     params={"messages": [message], "message_globals": message_globals})
        log.info("Message sent successfully.")
        return response

    def get_status(self, request_id: str):
        """
        Get the status for a viber message request.
        :param params:
        request_id : str - The request ID of the viber message request.
        :return:
        """
        response = self._client.get(
            self._client.host(),
            f"/report/v1/viber-log/{request_id}"
        )
        log.info("Message status retrieved successfully.")
        return response
