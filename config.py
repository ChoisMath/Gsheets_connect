import configparser

import streamlit as st

env_config = configparser.ConfigParser()
env_config.read('.streamlit/config.ini', encoding='utf-8')

api_key = st.secrets["solapi_api_key"]
api_secret = st.secrets["solapi_api_secret"]
protocol = 'https'
domain = 'api.solapi.com'
prefix = ''


def get_url(path):
    url = '%s://%s' % (protocol, domain)
    if prefix != '':
        url = url + prefix
    url = url + path
    return url


import time
import datetime
import uuid
import hmac
import hashlib


def unique_id():
    return str(uuid.uuid1().hex)


def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


def get_signature(key='', msg=''):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def get_headers(api_key='', api_secret_key=''):
    date = get_iso_datetime()
    salt = unique_id()
    data = date + salt
    return {
        'Authorization': 'HMAC-SHA256 ApiKey=' + api_key + ', Date=' + date + ', salt=' + salt + ', signature=' +
                         get_signature(api_secret_key, data),
        'Content-Type': 'application/json; charset=utf-8'
    }
