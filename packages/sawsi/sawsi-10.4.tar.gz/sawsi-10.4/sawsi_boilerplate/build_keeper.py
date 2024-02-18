"""
빌드 준비에 필요한 코드 호출
샘플입니다. 적절히 변경해서 사용해주세요.
"""


import api
import config
import {{app}}.doc_make.test_and_make_api_doc
from {{app}}.model.sample_user import Address, User


if __name__ == '__main__':
    config.build = True
    # DB 초기화 등 진행.
    Address.sync_table()
    User.sync_table()

    if config.env == 'dev':
        {{app}}.doc_make.test_and_make_api_doc.test_and_make_api_doc()
