import logging

log = logging.getLogger(__name__)


class NUMBER_LOOKUP:

    def __init__(self, client):
        self._client = client

    def search_number_details(self, recipient: str):
        """
        Search number details.
        :param params: dict - The search request parameters.
        :return:
        """
        params = {
            "recipient": recipient
        }
        response = self._client.post(self._client.host(), "/hlr/v1/lookup", params=params)
        log.info("Search request is success.")
        return response
