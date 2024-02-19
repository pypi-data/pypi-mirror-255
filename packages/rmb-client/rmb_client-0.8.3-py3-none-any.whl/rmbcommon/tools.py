import uuid
import base62
import time
from datetime import datetime


def format_time_ago(unix_timestamp) -> str:
    """
    Convert a Unix timestamp to a user-friendly time string.
    """
    try:
        unix_timestamp = int(unix_timestamp)
    except:
        return unix_timestamp

    now = int(time.time())
    unix_timestamp = int(unix_timestamp)
    diff = now - unix_timestamp

    # Time calculations
    minute = 60
    hour = 60 * minute
    day = 24 * hour

    if diff < hour:
        return f"{diff // minute} minutes ago" if diff >= minute else "Just now"
    elif diff < day:
        hours = diff // hour
        minutes = (diff % hour) // minute
        return f"{hours} hours {minutes} minutes ago" if minutes else f"{hours} hours ago"
    elif diff < 3 * day:
        return f"{diff // day} days ago"
    else:
        # Convert to specific date and time format for durations longer than 3 days
        return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')

def gen_base62_uuid():
    # 生成一个 UUID
    my_uuid = uuid.uuid4()
    # 转换 UUID 的整数表示为 Base62
    base62_uuid = base62.encode(int(my_uuid))
    return base62_uuid


def gen_uuid_for_vector():
    return str(uuid.uuid1())


def gen_tenant_id():
    return f"t_{gen_base62_uuid()}"

def gen_token_id():
    return f"token_{gen_base62_uuid()}"


def gen_datasource_id():
    return f"ds_{gen_base62_uuid()}"


def gen_id_for_chat():
    return f"chat_{gen_base62_uuid()}"


def gen_id_for_msg():
    return f"msg_{gen_base62_uuid()}"


def gen_id_for_run():
    return f"run_{gen_base62_uuid()}"


def gen_excel_file_id():
    return f"excel_{gen_base62_uuid()}"

def gen_img_file_id():
    return f"img_{gen_base62_uuid()}"

