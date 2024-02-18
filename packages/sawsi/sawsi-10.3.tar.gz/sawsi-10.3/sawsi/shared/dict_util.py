"""
dict 관련 유틸
"""
from decimal import Decimal


def convert_number_to_decimal(dict_detail):
    for key, value in dict_detail.items():
        if isinstance(value, float):
            dict_detail[key] = Decimal(str(value))
        elif isinstance(dict_detail[key], dict):
            convert_number_to_decimal(dict_detail[key])
        elif isinstance(dict_detail[key], list):
            for item in dict_detail[key]:
                if isinstance(item, dict):
                    convert_number_to_decimal(item)
    return dict_detail


def convert_decimal_to_number(dict_detail):
    for key, value in dict_detail.items():
        if isinstance(value, Decimal):
            if value % 1 == 0:
                dict_detail[key] = int(value)
            else:
                dict_detail[key] = float(value)
        elif isinstance(dict_detail[key], dict):
            convert_decimal_to_number(dict_detail[key])
        elif isinstance(dict_detail[key], list):
            for item in dict_detail[key]:
                if isinstance(item, dict):
                    convert_decimal_to_number(item)
    return dict_detail


if __name__ == '__main__':
    # r = get_value_by_dot_representation({'a': {'b': {'c': {'d': 'e'}}}}, 'a')
    # print(r)
    print(convert_number_to_decimal({
        'd': {
            'd': {
                '1': 14.232,
                'd': 'ss'
            },
            's': {
                'g': 'sss'
            },
            'ss': [
                {
                    'ok': 1.141,
                    'ss': 'ssss'
                }
            ]
        }
    }))