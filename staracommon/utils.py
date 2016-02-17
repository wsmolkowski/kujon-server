import settings

import httplib2
import socks


def get_proxy():
    if settings.PROXY_PORT and settings.PROXY_URL:
        return httplib2.ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host=settings.PROXY_URL, proxy_port=settings.PROXY_PORT, proxy_rdns=False)
    return None