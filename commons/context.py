from tornado.util import ObjectDict

from commons import utils
from commons.SocialCaller import SocialCaller
from commons.UsosCaller import UsosCaller, AsyncCaller
from commons.constants import fields


class Context(ObjectDict):
    def __init__(self, config, user_doc=None, usos_doc=None, refresh=False, remote_ip=None, http_client=None,
                 io_loop=None):

        self.settings = None

        self.config = config
        self.user_doc = user_doc
        self.usos_doc = usos_doc
        self.refresh = refresh
        self.remote_ip = remote_ip
        self.prepare_curl_callback = self.config.PREPARE_CURL_CALLBACK
        self.proxy_host = self.config.PROXY_HOST
        self.proxy_port = self.config.PROXY_PORT

        if not http_client:
            http_client = utils.http_client(self.proxy_host, self.proxy_port, io_loop)

        self.http_client = http_client
        self.socialCaller = SocialCaller(self.http_client, self.proxy_host, self.proxy_port)

        if user_doc and usos_doc:
            self.setUp()

    def setUp(self):
        if self.usos_doc and self.user_doc:
            self.consumer_token = dict(key=self.usos_doc[fields.CONSUMER_KEY],
                                       secret=self.usos_doc[fields.CONSUMER_SECRET])

            if fields.ACCESS_TOKEN_KEY in self.user_doc and fields.ACCESS_TOKEN_SECRET in self.user_doc:
                self.access_token = dict(key=self.user_doc[fields.ACCESS_TOKEN_KEY],
                                         secret=self.user_doc[fields.ACCESS_TOKEN_SECRET])

                self.usosCaller = UsosCaller(self.usos_doc[fields.USOS_URL], self.http_client, self.config.PROXY_HOST,
                                             self.config.PROXY_PORT, self.remote_ip, self.consumer_token,
                                             self.access_token,
                                             self.prepare_curl_callback)

        if self.usos_doc:
            self.asyncCaller = AsyncCaller(self.usos_doc[fields.USOS_URL], self.http_client, self.config.PROXY_HOST,
                                           self.config.PROXY_PORT, self.remote_ip, self.prepare_curl_callback)
