# 프로젝트 제목

**간략한 설명**: 
AWS 의 boto3 를 Wrapping 하여 손쉽게 DynamoDB, S3, SecretManager 등의 서비스를 활용할 수 있도록 만든 라이브러리입니다.
추가적으로 DynamoDB의 경우 One-Big-Table 구조를 차용하여, 하나의 테이블에서 여러개의 파티션을 관리할 수 있도록 구현하였습니다.
또한 S3의 경우 파일을 올리면 URL로 자동으로 뽑아주는 등의 유용한 기능들이 포함되어 있습니다.
추가적으로 AWS API Gateway 와 Lambda 의 연결을 원활하게 해주는 핸들러 유틸이 포함되어 있습니다.
## 시작하기

```bash
pip install sawsi
```

## 주의사항
DynamoDB 의 경우 Pure 한 구성이 아닌, ORM 형식으로 데이터 구조를 변형하여 저장하기 때문에, 기존 사용하던 DB에 덮어 사용시 충돌이 생길 수 있으니 새로운 DDB 객체를 생성하여 사용함을 권장드립니다.

## 프로젝트 사용방법

메인 SAWSI API 사용 방법
```python
from awssi.aws.dynamodb.api import DyanmoFDBAPI
db_api = DyanmoFDBAPI('ddb_name')
items = db_api.fdb_generate_items('partition_name')
for item in items:
  print(item)
  
# 위와 같은 방법으로 S3, SMS, CodeCommit, SecretManager API 를 사용하실 수 있습니다.
```

유틸리티성 핸들러, 함수, 해시 등 기능
```python
from sawsi.shared import error_util
from sawsi.shared import handler_util

# 아래 핸들러는 share.error_util.AppError 에러가 발생할시에, 자동으로
# 에러를 response 객체에 담아 코드와 메시지로 구분하여 전송합니다.
@handler_util.aws_handler_wrapper(
    error_receiver=lambda errmsg: print(errmsg),  # 이 Lambda 함수를 슬랙 Webhook 등으로 대체하면 에러 발생시 모니터링이 가능합니다.
    content_type='application/json',  # 기본적으로 JSON 타입을 반환합니다.
    use_traceback=True,  # 에러 발생시 상세 값을 응답에 전달할지 유무입니다.
)
def some_api_aws_lambda_handler(event, context):
    """
    AWS LAMBDA에서 API Gateway 를 통해 콜한 경우
    """
    # API Gateway 로부터 Lambda 에 요청이 들어오면 다음과 같이 body 와 headers 를 분리하여 dict 형태로 반환합니다.
    body = handler_util.get_body(event, context)
    headers = handler_util.get_headers(event, context)
    
    # 아래부터는 사용자가 직접 응용하여 핸들러를 구성, 다른 함수들로 라우팅합니다.
    cmd = body['cmd']
    if cmd == 'member.request_login':
        import member
        return member.request_login(
            mid=body['mid'],
            mpw=body['pwd'],
        )
    
    # 핸들러 CMD 에 해당하는 CMD 값이 없을 경우 에러 발생
    raise error_util.SYSTEM_NO_SUCH_CMD
```

DynamoFDBAPI 의 apply_partition_map 기능 사용
* 이 기능을 통해, 파티션 구성을 한번에 마이그레이션할 수 있습니다. 예를 들면 개발환경에서 쓰던 구성을 한번에 프로덕션으로 가져갈 수 있습니다.
* 배포 전에 작동하는 스크립트를 구현해놓고 사용하시는것을 권장합니다.
```python
# DynamoFDBAPI 객체 생성
from sawsi.aws.dynamodb.api import DynamoFDBAPI
fdb_api = DynamoFDBAPI('<your_table_name>')

# 파티션 맵 정의
fdb_partition_map = {
    'your_partition_name': {
        'pk': '<primary_key_name>',
        'sk': '<sort_key_name>',
        'uks': ['<optional_unique_key1>', '<optional_unique_key2>'],
        'indexes': [
            {'pk': '<primary_key_name>', 'sk': '<sort_key_name>'},
            {'pk': '<another_primary_key_name>', 'sk': '<another_sort_key_name>'},
            # ... 여러 인덱스 정의
        ]
    },
    # ... 다른 파티션 정의
}

# 파티션 맵 적용
fdb_api.apply_partition_map(fdb_partition_map)
```


배포 자동화 기능 사용
AWS CodeCommit 및 CodeBuild, CodePipeline 를 세팅했다는 가정 하에,
build_spec.yml 파일을 다음과 같이 작성하여 AWS CodeCommit 에 커밋시 
자동으로 원하는 Lambda 에 배포가 되도록 만들 수 있습니다.
> build_spec.yml 파일 구성 (AWS CodeBuild 설정에서 파일명 지정 가능)
```yaml
version: 0.2
# AWS Codebuild 환경 > 이미지 구성 > amazon/aws-lambda-python:3.11
# https://hub.docker.com/r/amazon/aws-lambda-python/tags 참고해서 정할 것

env:
  variables:
    ARN_BASE: "arn:aws:lambda:us-west-1:{ARN_NUMBER}"
    # 아래에 배포할 Lambda 속성들을 리스트업합니다.
    LAMBDAS: |
      [
        {"name": "dev_usa_serverless_main", "handler": "l0_endpoint.main.handler"},
        {"name": "dev_usa_serverless_scheduler", "handler": "l0_endpoint.scheduler.handler"},
        {"name": "dev_usa_serverless_admin", "handler": "l0_endpoint.admin.handler"},
        {"name": "dev_usa_serverless_plaid_webhook", "handler": "l0_endpoint.plaid_webhook.handler"},
        {"name": "dev_usa_serverless_queue_worker", "handler": "l0_endpoint.queue_worker.handler"}
      ]
    # 필요하면 추가..
    RUNTIME: "python3.11"
    MEM_SIZE: "2048"
    S3_BUCKET: "dev-build"


phases:
  pre_build:
    commands:
      - export DATE=$(date +%Y%m%d%H%M%S)
  install:
    commands:
      - echo Installing required tools...
      - yum install unzip -y
      - yum install -y zip
      - yum install -y jq
      # x86_64 혹은 arm 중에 선택합니다.
      - curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
#      - curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
      - mkdir awscliv2
      - unzip awscliv2.zip -d awscliv2
      - ./awscliv2/aws/install
      - aws --version
      - rm -rf awscliv2
      - rm -rf awscliv2.zip

  build:
    commands:
      - echo Build started on `date`
      - echo Installing requirements...
      - pip install -r requirements.txt -t .
      - echo Zipping the project...
      - zip -r function.zip .
      - cp function.zip ../function.zip
      - python3 build_keeper.py
      - echo Uploading to S3...
      - aws s3 cp function.zip s3://$S3_BUCKET/$DATE/function.zip

  post_build:
     commands:
       - |
          for row in $(echo "${LAMBDAS}" | jq -r '.[] | @base64'); do
            _jq() {
              echo ${row} | base64 --decode | jq -r ${1}
            }
    
            LAMBDA_FUNCTION_NAME=$(_jq '.name')
            HANDLER=$(_jq '.handler')
            
            sleep 1
            aws lambda update-function-configuration --function-name $LAMBDA_FUNCTION_NAME --runtime $RUNTIME --handler $HANDLER --memory-size $MEM_SIZE --description DeployByCodebuild 
            sleep 1
            aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --s3-bucket $S3_BUCKET --s3-key $DATE/function.zip
            sleep 1
            aws lambda publish-version --function-name $LAMBDA_FUNCTION_NAME
          done

artifacts:
  files:
    - function.zip
  discard-paths: yes


```