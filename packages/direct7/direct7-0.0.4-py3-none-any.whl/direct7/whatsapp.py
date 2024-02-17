import logging

log = logging.getLogger(__name__)


class WHATSAPP:

    def __init__(self, client):
        self._client = client

    def send_whatsapp_freeform_message(self, originator: str, recipient: str, message_type: str, first_name: str = None,
                                       last_name: str = None, display_name: str = None, phone: str = None,
                                       email: str = None, url: str = None, latitude: str = None, longitude: str = None,
                                       location_name: str = None, location_address: str = None,
                                       attachment_type: str = None, attachment_url: str = None,
                                       attachment_caption: str = None, message_text: str = None):
        """
        Send a WhatsApp message to a single/multiple recipients.
        :param originator: str - The message originator.
        :param recipient: str - The message recipient.
        :param message_type: str - The type of message ("CONTACTS", "LOCATION", "ATTACHMENT", "TEXT").
        :param first_name: str - First name for "CONTACTS" message type.
        :param last_name: str - Last name for "CONTACTS" message type.
        :param display_name: str - Display name for "CONTACTS" message type.
        :param phone: str - Phone number for "CONTACTS" message type.
        :param email: str - Email address for "CONTACTS" message type.
        :param url: str - URL for "CONTACTS" message type.
        :param latitude: str - Latitude for "LOCATION" message type.
        :param longitude: str - Longitude for "LOCATION" message type.
        :param location_name: str - Location name for "LOCATION" message type.
        :param location_address: str - Location address for "LOCATION" message type.
        :param attachment_type: str - Attachment type for "ATTACHMENT" message type.
        :param attachment_url: str - Attachment URL for "ATTACHMENT" message type.
        :param attachment_caption: str - Attachment caption for "ATTACHMENT" message type.
        :param message_text: str - Message text for "TEXT" message type.
        """
        message = {
            "originator": originator,
            "recipients": [{"recipient": recipient}],
            "content": {
                "message_type": message_type
            }
        }

        if message_type == "CONTACTS":
            message["content"]["contact"] = {
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name,
                "phone": phone,
                "email": email,
                "url": url
            }
        elif message_type == "LOCATION":
            message["content"]["location"] = {
                "latitude": latitude,
                "longitude": longitude,
                "name": location_name,
                "address": location_address
            }
        elif message_type == "ATTACHMENT":
            message["content"]["attachment"] = {
                "attachment_type": attachment_type,
                "attachment_url": attachment_url,
                "attachment_caption": attachment_caption
            }
        elif message_type == "TEXT":
            message["content"]["message_text"] = message_text

        response = self._client.post(self._client.host(), "/whatsapp/v1/send", params={"messages": [message]})
        log.info("Message sent successfully.")
        return response

    def send_whatsapp_templated_message(self, originator: str, recipient: str, template_id: str,
                                        body_parameter_values: dict, media_type: str = None, media_url: str = None,
                                        latitude: str = None, longitude: str = None, location_name: str = None,
                                        location_address: str = None):
        """
        Send a WhatsApp message to a single/multiple recipients.
        :param originator: str - The message originator.
        :param recipient: str - The message recipient.
        :param template_id: str - The template ID for text messages.
        :param body_parameter_values: dict - The body parameter values for text templates.
        :param media_type: str - The type of media (e.g., "image", "video").
        :param media_url: str - The URL of the media content.
        """
        message = {
            "originator": originator,
            "recipients": [{"recipient": recipient}],
            "content": {
                "message_type": "TEMPLATE",
                "template": {"template_id": template_id, "body_parameter_values": body_parameter_values}
            }
        }

        if media_type:
            if media_type == "location":
                message["content"]["template"]["media"] = {
                    "media_type": "location",
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "name": location_name,
                        "address": location_address
                    }
                }
            else:
                message["content"]["template"]["media"] = {"media_type": media_type, "media_url": media_url}

        response = self._client.post(self._client.host(), "/whatsapp/v1/send", params={"messages": [message]})
        log.info("Message sent successfully.")
        return response

    def get_status(self, request_id: str):
        """
        Get the status for a whatsapp message request.
        :param params:
        request_id : str - The request ID of the whatsapp message request.
        :return:
        """
        response = self._client.get(
            self._client.host(),
            f"/whatsapp/v1/report/{request_id}"
        )
        log.info("Message status retrieved successfully.")
        return response
