
class SMS:
    def __init__(self, boto3_session, region_name='us-east-1'):
        self.client = boto3_session.client('sns', region_name=region_name)
        self.region = boto3_session.region_name

    def send_sms(self, phone, message):
        response = self.client.response = self.client.publish(
            PhoneNumber=phone,  # 실제 전화번호로 변경
            Message=message,
        )
        return response
