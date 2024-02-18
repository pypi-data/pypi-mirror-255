"""
빌드 준비에 필요한 코드 호출
"""


import api
import config
import {{app}}.doc_make.test_and_make_api_doc


if __name__ == '__main__':
    config.build = True
    # DB 초기화 등 진행. 개발 환경에서 진행됩니다.
    if config.env == 'dev':
        {{app}}.doc_make.test_and_make_api_doc.test_and_make_api_doc()
