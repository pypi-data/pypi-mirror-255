import logging

log = logging.getLogger(__name__)


class SLACK:

    def __init__(self, client):
        self._client = client

    def send_slack_message(self, content: str, work_space_name: str, channel_name: str, report_url: str = None):
        """
        Send a slack message to a single workspace.
        :param content: str -  Message content is being sent.
        :param work_space_name: str - Name of Workspace to send message.
        :param channel_name: str - Name of Channel to send message.
        :param report_url: str - receive delivery status.
        :return:
        """
        message = {
            "channel": "slack",
            "content": content,
            "work_space_name": work_space_name,
            "channel_name": channel_name
        }
        message_globals = {
            "report_url": report_url
        }
        response = self._client.post(self._client.host(), "/messages/v1/send",
                                     params={"messages": [message], "message_globals": message_globals})

        log.info("Message sent successfully.")
        return response

    def get_status(self, request_id: str):
        """
        Get the status for a slack message request.
        :param params:
        request_id : str - The request ID of the slack message request.
        :return:
        """
        response = self._client.get(
            self._client.host(),
            f"/report/v1/message-log/{request_id}"
        )
        log.info("Message status retrieved successfully.")
        return response
