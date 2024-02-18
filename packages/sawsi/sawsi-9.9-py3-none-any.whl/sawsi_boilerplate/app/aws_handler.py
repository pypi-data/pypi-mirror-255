import time

from sawsi.shared import error_util
from sawsi.shared import handler_util
import errs


# 아래 핸들러는 share.error_util.AppError 에러가 발생할시에, 자동으로
# 에러를 response 객체에 담아 코드와 메시지로 구분하여 전송합니다.
@handler_util.aws_handler_wrapper(
    error_receiver=lambda errmsg: print(errmsg),  # 이 Lambda 함수를 슬랙 Webhook 등으로 대체하면 에러 발생시 모니터링이 가능합니다.
    content_type='application/json',  # 기본적으로 JSON 타입을 반환합니다.
    use_traceback=True,  # 에러 발생시 상세 값을 응답에 전달할지 유무입니다.
    ignore_app_errors=[
        errs.no_session
    ]
)
def handler(event, context):
    """
    AWS LAMBDA에서 API Gateway 를 통해 콜한 경우
    """
    # API Gateway 로부터 Lambda 에 요청이 들어오면 다음과 같이 body 와 headers 를 분리하여 dict 형태로 반환합니다.
    body = handler_util.get_body(event, context)
    headers = handler_util.get_headers(event, context)
    source_ip = handler_util.get_source_ip(event, context)

    # 아래부터는 사용자가 직접 응용하여 핸들러를 구성, 다른 함수들로 라우팅합니다.
    cmd = body.get('cmd', None)

    # 로그인을 수행하는 API
    if cmd == '{{app}}.controller.sample_login.login':
        import {{app}}.controller.sample_login
        return {{app}}.controller.sample_login.login(
            body['email'], body['password']
        )
    # ... 세션 할당 이전 구현할 수 있는 API 들을 구현


    # 헤더로부터 세션 가져오기
    session_id = headers.get('session_id', None)
    if not session_id:
        raise errs.no_session

    # 아래부터는 세션이 있어야 활용 가능한 API 구현

    # 자기 자신의 정보를 세션으로 가져오는 API
    if cmd == '{{app}}.controller.sample_login.get_me':
        import {{app}}.controller.sample_login
        return {{app}}.controller.sample_login.get_me(
            session_id
        )

    # 핸들러 CMD 에 해당하는 CMD 값이 없을 경우 에러 발생
    raise error_util.SYSTEM_NO_SUCH_CMD
