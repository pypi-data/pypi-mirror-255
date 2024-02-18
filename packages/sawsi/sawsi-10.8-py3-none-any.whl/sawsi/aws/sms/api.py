from sawsi.aws import shared
from sawsi.aws.sms import wrapper


class SMSAPI:
    """
    SMS 전송 API
    """
    def __init__(self, region_name, credentials=None):
        """
        :param bucket_name:
        :param credentials: {
            "aws_access_key_id": "str",
            "aws_secret_access_key": "str",
            "region_name": "str",
            "profile_name": "str",
        }
        """
        self.boto3_session = shared.get_boto_session(credentials)
        self.region_name = region_name
        self.sms = wrapper.SMS(self.boto3_session, region_name)

    def send_sms(self, phone, message):
        response = self.sms.send_sms(phone, message)
        return response
