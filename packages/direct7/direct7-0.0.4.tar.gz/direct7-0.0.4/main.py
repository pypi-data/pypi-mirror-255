from direct7 import Client

if __name__ == "__main__":
    client = Client(api_token="Your API Token")

result = client.sms.send_message({"recipients": ["+9199XXXXXXXX"], "content": "Greetings from D7 API", "unicode": False},
                                 originator="Sender",
                                 report_url="https://the_url_to_receive_delivery_report.com",
                                 )
print(result)
