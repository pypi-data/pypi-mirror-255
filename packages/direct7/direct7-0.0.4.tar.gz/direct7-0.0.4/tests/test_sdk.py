from src.direct7 import Client

client = Client(
    api_token='Your API Token')


def test_send_messages():
    response_send_messages = client.sms.send_messages(
        {"recipients": ["+9199XXXXXXXXXX"],"content": "مرحبا بالعالم!", "unicode": True},
        originator="Sender",
        report_url="https://the_url_to_receive_delivery_report.com",
        schedule_time='2024-02-05T09:48:42+0000',
        )

    assert response_send_messages is not None
    assert response_send_messages


def test_get_status():
    response_get_status = client.sms.get_status(request_id="00152e17-1717-4568-b793-bd6c729c1ff3")
    print(response_get_status)
    assert response_get_status is not None
    assert response_get_status
