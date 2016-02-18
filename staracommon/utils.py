import httplib2
import socks
import datetime
from bson.objectid import ObjectId

import settings
import constants


def get_proxy():
    if settings.PROXY_PORT and settings.PROXY_URL:
        return httplib2.ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host=settings.PROXY_URL, proxy_port=settings.PROXY_PORT, proxy_rdns=False)
    return None


def serialize_dictionary(data):
    for key, value in data.items():
        if isinstance(value, list):
            data[key] = serialize_list(value)
        elif isinstance(value, dict):
            data[key] = serialize_dictionary(value)
        elif isinstance(value, datetime.datetime):
            data[key] = value.strftime(constants.DATETIME_DISPLAY_FORMAT)
        elif isinstance(value, ObjectId):
            data.pop(key)
    return data


def serialize_list(data):
    result = []
    for element in data:
        if isinstance(element, list):
            result.append(serialize_list(element))
        elif isinstance(element, dict):
            result.append(serialize_dictionary(element))
        elif isinstance(element, datetime.datetime):
            result.append(element.strftime(constants.DATETIME_DISPLAY_FORMAT))
        elif isinstance(element, ObjectId):
            continue
        else:
            result.append(element)
    return result


def serialize(data):
    if isinstance(data, list):
        return serialize_list(data)
    elif isinstance(data, dict):
        return serialize_dictionary(data)

    return data
