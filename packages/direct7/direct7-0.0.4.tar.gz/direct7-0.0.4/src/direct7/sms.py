import logging

log = logging.getLogger(__name__)


class SMS:

    def __init__(self, client):
        self._client = client

    def send_messages(self, *args, originator: str, report_url: str = None, schedule_time: str = None):
        """
        Send one or more messages to a single/multiple recipient(s).
        :param args: variable number of message dictionaries.
                      Each message dictionary should contain the following fields:
                        - recipients: list - Mobile Numbers to send SMS separated by comma in an array.
                        - content: str - The message content being sent.
                        - msg_type: str - Type of the message (e.g., "text").
                        - data_coding: str - Coding type for the message (e.g., "text" or "unicode").
        :param originator: str - The Sender/Header of a message.
        :param report_url: str - Receive delivery status.
        :return:
        """

        messages = [
            {
                "channel": "sms",
                "recipients": message.get("recipients", []),
                "content": message.get("content", ""),
                "msg_type": "text",
                "data_coding": "unicode" if message.unicode else "text"
            }
            for message in args
        ]
        message_globals = {
            "originator": originator,
            "report_url": report_url,
            "schedule_time": schedule_time
        }
        payload = {
            "messages": messages,
            "message_globals": message_globals
        }
        response = self._client.post(self._client.host(), "/messages/v1/send", params=payload)
        log.info("Messages sent successfully.")
        return response

    def get_status(self, request_id: str):
        """
        Get the status for a message request.
        :param params:
        request_id : str - The request ID of the message request.
        :return:
        """
        response = self._client.get(
            self._client.host(),
            f"/report/v1/message-log/{request_id}"
        )
        log.info("Message status retrieved successfully.")
        return response
