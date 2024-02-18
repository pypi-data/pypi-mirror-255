from datetime import datetime, timezone
import json
import ipaddress
import uuid
import math
import socket
from bson import ObjectId
from logging import FileHandler
import logging
import contextlib
import sys

start_time = None
logger = None
handler = None


def passed_midnight(delta=1):
    current_time = datetime.datetime.now().time()
    target_time = datetime.time(0, delta)
    return current_time >= target_time


def date_equals_today(date_to_check):
    return date_to_check.date() == datetime.datetime.today().date()


def check_logger(log_caption, log_file_name):
    global start_time
    global logger
    global handler

    if logger:
        write_info_log("{timestamp}: Checking logger".format(timestamp=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")))

    if not start_time or (passed_midnight(10) and not date_equals_today(start_time)):  # Every day restart logging
        if not logger:
            logger = logging.getLogger(log_caption)
        if handler:
            logger.removeHandler(handler)

        logger.setLevel(logging.DEBUG)
        handler = FileHandler(log_file_name, mode='a')
        logger.addHandler(handler)

        if start_time:
            write_info_log("{timestamp}: Logging restarted".format(timestamp=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")))

        start_time = datetime.datetime.now()


def write_info_log(msg):
    if msg:
        try:
            logger.info(msg)
            print(msg)
        except Exception as e:
            print(e)


def write_error_log(msg):
    if msg:
        try:
            logger.error(msg)
            print(msg)
        except Exception as e:
            print(e)


@contextlib.contextmanager
def stdout_redirect(where):
    sys.stdout = where
    try:
        yield where
    finally:
        sys.stdout.flush()
        sys.stdout = sys.__stdout__


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, bytes):
            return o.decode('utf-8')
        elif isinstance(o, Exception):
            return str(o)
        elif isinstance(o, KeyError):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return str(z)
        elif isinstance(z, uuid.UUID):
            return str(z)
        elif isinstance(z, ipaddress.IPv4Address):
            return str(z)
        elif isinstance(z, ObjectId):
            return str(z)
        else:
            return super().default(z)


def get_epoch_now():
    return math.floor((datetime.now(timezone.utc) - datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)).total_seconds() * 1000)


def get_now():
    return math.floor(datetime.now(timezone.utc).timestamp() * 1000)


def get_utc_now():
    return datetime.now(timezone.utc)


def add_to_now(secs):
    return math.floor((datetime.now(timezone.utc).timestamp() + secs) * 1000)


def add_to_epoch_now(secs):
    return math.floor(((datetime.now(timezone.utc) - datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)).total_seconds() + secs) * 1000)


def do_log(req_data, *log_messages):
    api_id = req_data["api_id"] if req_data.get("api_id") else "None"
    msg = "{timestamp}: {log_messages} - (API_ID: {api_id})".format(api_id=api_id, log_messages=log_messages, timestamp=datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
    print(msg)


def send_via_udp(req_data, message, ip, port):
    if not message or not ip or not port:
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        message_str = json.dumps(message, cls=JSONEncoder)
        do_log(req_data, message_str)
        sock.sendto(str.encode(message_str,), (ip, port))
    except Exception as err:
        do_log(req_data, err)
    finally:
        sock.close()
