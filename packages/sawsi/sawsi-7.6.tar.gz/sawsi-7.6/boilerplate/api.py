from sawsi.aws.secrets_manager.api import SecretManagerAPI
from sawsi.aws.dynamodb.api import DynamoDBAPI
from sawsi.aws.s3.api import S3API
from sawsi.aws.locking.api import LockingAPI
from sawsi.aws.firehose.api import Firehose
from sawsi.aws.ses.api import SESAPI
from sawsi.aws.sqs.api import SQSAPI
import os


env = os.getenv('env')  # prod or dev
region = 'ap-northeast-2'

if not env:
    raise Exception('os.getenv() is None')


app_name = '{{app}}'

secret_manager: SecretManagerAPI = SecretManagerAPI(f'{env}/{app_name}', region=region)
dynamo = DynamoDBAPI(f'{env}-{app_name}', region=region)
s3_public = S3API(f'{env}-{app_name}-public', region=region)

locking = LockingAPI(f'{env}-{app_name}-locking', region=region)
firehose_log = Firehose(f'{env}-{app_name}', f'{env}-{app_name}-firehose', 'log', region=region)

ses = SESAPI(region=region)
sqs = SQSAPI(f'https://sqs.{region}.amazonaws.com/<aws_account_id>/{env}-ws-queue', region=region)
