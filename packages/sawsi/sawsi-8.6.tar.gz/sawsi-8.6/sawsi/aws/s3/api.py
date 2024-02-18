from sawsi.aws import shared
from sawsi.aws.s3 import wrapper
from secrets import token_urlsafe
from sawsi.shared import error_util
import json


def make_query(base_query, idx_offset=0, limit=100):
    # 기존 쿼리에서 WHERE 절이 있는지 확인합니다.
    if 'WHERE' in base_query or 'where' in base_query:
        # 이미 WHERE 절이 있다면, 기존 조건에 AND 연산자를 추가합니다.
        modified_query = f"{base_query} AND s._idx >= {idx_offset} LIMIT {limit}"
    else:
        # WHERE 절이 없다면, 새로운 WHERE 절을 추가합니다.
        if 'FROM' in base_query or 'from' in base_query:
            # FROM 절이 있다면, WHERE 절을 FROM 절 바로 뒤에 추가합니다.
            parts = base_query.split('FROM', 1)
            modified_query = f"{parts[0]} FROM {parts[1].strip()} WHERE s._idx >= {idx_offset} LIMIT {limit}"
        else:
            # FROM 절도 없다면, 쿼리가 잘못되었다고 가정하고 에러를 발생시킵니다.
            raise ValueError("Invalid SQL query. 'FROM' clause not found.")

    return modified_query


class S3API:
    """
    S3 를 활용하는 커스텀 ORM 클래스
    """
    def __init__(self, bucket_name, credentials=None, region=shared.DEFAULT_REGION):
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
        self.cache = {}
        self.bucket_name = bucket_name
        self.s3 = wrapper.S3(self.boto3_session, region=region)

    def init_s3_bucket(self, acl='private'):
        """
        실제 버킷 생성
        :return:
        """
        return self.s3.init_bucket(self.bucket_name, acl)

    def upload_binary(self, file_name, binary):
        return self.s3.upload_binary(self.bucket_name, file_name, binary)

    def delete_binary(self, file_name):
        return self.s3.delete_binary(self.bucket_name, file_name)

    def download_binary(self, file_name):
        return self.s3.download_binary(self.bucket_name, file_name)

    def upload_file_and_return_url(self, file_bytes, extension, content_type, use_accelerate=False, forced_file_id=None):
        """
        파일을 업로드하고 URL 을 반환합니다.
        만천하에 공개되기 때문에 공개해도 괜찮은 파일만 사용해야 함.
        :param file_bytes:
        :param extension:
        :param content_type:
        :param use_accelerate:
        :param forced_file_id: str (이거 있으면 이걸로 강제로 덮어씌움)
        :return:
        """
        if use_accelerate:
            base_url = f'https://{self.bucket_name}.s3-accelerate.amazonaws.com/'  # 전송 가속화
        else:
            base_url = f'https://{self.bucket_name}.s3.{self.s3.region}.amazonaws.com/'

        if forced_file_id:
            file_id = forced_file_id
        else:
            file_id = f'{token_urlsafe(32)}.{extension}'
        response = self.s3.upload_file(self.bucket_name, file_bytes, file_id, content_type, 'public-read')
        return base_url + file_id

    def upload_items_for_select(self, file_name: str, item_list: [dict]):
        """
        Select Query 를 위해서 JSON LIST 로 만들어서 업로드합니다.
        :param file_name:
        :param item_list: [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35}
        ]
        :return:
        """
        # item_list의 타입을 확인하여 리스트인지 확인
        if not isinstance(item_list, list):
            raise ValueError("item_list은 리스트 타입이어야 합니다.")

        # item_list의 각 항목이 딕셔너리인지 확인
        for idx, item in enumerate(item_list):
            if not isinstance(item, dict):
                raise ValueError("item_list의 각 항목은 딕셔너리 타입이어야 합니다.")

        # item 에 _idx 를 매깁니다. 쿼리 순서 보장용
        json_string = '\n'.join([json.dumps(item) for item in item_list])
        response = self.upload_binary(file_name, json_string.encode('utf-8'))
        return response

    def list_objects_v2(self, prefix, continuation_token, start_after=None, limit=1000):
        """
        버킷에 있는 객체들을 순환
        :param continuation_token:
        :param start_after:
        :param limit:
        :return:
        """
        response = self.s3.list_objects_v2(bucket_name=self.bucket_name,
                                           prefix=prefix,
                                           limit=limit,
                                           start_after=start_after,
                                           continuation_token=continuation_token)
        return response

    def generate_object_keys(self, prefix, start_after=None, limit=1000):
        continuation_token = None
        response = self.list_objects_v2(prefix, continuation_token, start_after, limit)
        continuation_token = response.get('NextContinuationToken', None)
        contents = response.get('Contents', [])
        for content in contents:
            yield content
        while continuation_token:
            response = self.list_objects_v2(prefix, continuation_token, start_after, limit)
            continuation_token = response.get('NextContinuationToken', None)
            contents = response.get('Contents', [])
            for content in contents:
                yield content

    def select(self, object_key, query):
        input_serialization = {'JSON': {'Type': 'DOCUMENT'}}
        output_serialization = {'JSON': {}}
        response = self.s3.select_object_content(self.bucket_name,
                                                 object_key=object_key,
                                                 query=query,
                                                 input_serialization=input_serialization,
                                                 output_serialization=output_serialization)
        return response


if __name__ == '__main__':
    s = S3API('')