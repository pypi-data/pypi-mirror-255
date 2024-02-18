import base64
import os
import traceback
from datetime import datetime, timezone


def get_unique_file_name_from_file_name(file_name: str):
    split_name = os.path.splitext(file_name)
    file_name = split_name[0]
    file_extension = split_name[1]
    now = utc_now_formatted_ymd_HMS()
    return f"{file_name}_{now}{file_extension}"


def decode_byte_array(byte_array: bytearray):
    return base64.b64encode(byte_array).decode('utf-8')


def utc_now_formatted():
    datetime_now_utc = datetime.now(tz=timezone.utc)
    return datetime_now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')


def utc_now_formatted_ymd():
    datetime_now_utc = datetime.now(tz=timezone.utc)
    return datetime_now_utc.strftime('%Y%m%d')


def utc_now_formatted_param(fmt: str):
    datetime_now_utc = datetime.now(tz=timezone.utc)
    return datetime_now_utc.strftime(f'%{fmt}')


def utc_now_formatted_ym():
    datetime_now_utc = datetime.now(tz=timezone.utc)
    return datetime_now_utc.strftime('%Y%m')


def utc_now_formatted_ymd_HMS():
    datetime_now_utc = datetime.now(tz=timezone.utc)
    return datetime_now_utc.strftime('%Y%m%d_%H%M%S')


def exception_to_string(ex):
    stack = traceback.extract_stack()[:-3] + traceback.extract_tb(ex.__traceback__)  # add limit=??
    pretty = traceback.format_list(stack)
    return ''.join(pretty) + '\n  {} {}'.format(ex.__class__, ex)


def is_weekend(time: datetime):
    week_day = time.weekday()
    if week_day < 5:
        return False
    else:  # 5 Sat, 6 Sun
        return True
