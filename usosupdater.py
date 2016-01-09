import json

import oauth2 as oauth

from helpers import log_execution_time, UsosException


URI_USER_INFO = "services/users/user?fields=id|first_name|last_name|student_status|sex|email|student_programmes|student_number|has_email|titles"
URI_CURSE_INFO = "services/courses/user?active_terms_only=false&fields=course_editions"


class USOSUpdater:

    def __init__(self, usosapi_base_url, consumer_key, consumer_secret, access_token_key, access_token_secret):

        self.usosapi_base_url = usosapi_base_url
        #usosapi_base_url_secure = usosapi_base_url.replace("http://", "https://")

        consumer = oauth.Consumer(consumer_key, consumer_secret)
        if access_token_key:
            access_token = oauth.Token(access_token_key, access_token_secret)
        else:
            raise UsosException("No access_token_key, do lepszej obslugi aby komorka sie zautoryzowala.")

        self.client = oauth.Client(consumer, access_token)

    @log_execution_time
    def request(self, url):

        resp, content = self.client.request(self.usosapi_base_url + url, 'GET')
        if resp['status'] != '200':
            raise UsosException('Invalid response %s.\n%s'.format(resp['status'], content))
        items = json.loads(content)

        return items

    def request_user_info(self):
        return self.request(URI_USER_INFO)

    def request_curse_info(self):
        return self.request(URI_CURSE_INFO)

