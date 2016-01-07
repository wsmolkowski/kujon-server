import json
from timeit import default_timer as timer

import oauth2 as oauth
import settings

#access_token_key = '3ShYQv8LyvgeXthKJzmJ'
#access_token_secret = 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'


class USOSUpdater:
    client = None

    def __init__(self, user_id, access_token_key, access_token_secret):
        if not (settings.usosapi_base_url and settings.consumer_key and settings.consumer_secret):
            raise Exception("Fill the settings first.")
        usosapi_base_url_secure = settings.usosapi_base_url.replace("http://", "https://")
        consumer = oauth.Consumer(settings.consumer_key, settings.consumer_secret)
        if access_token_key:
            access_token = oauth.Token(access_token_key, access_token_secret)
        else:
            raise Exception("No access_token_key, do lepszej obslugi aby komorka sie zautoryzowala.")

        self.client = oauth.Client(consumer, access_token)

    def request(self, url):
        start = timer()
        resp, content = self.client.request(settings.usosapi_base_url + url, "GET")
        if resp['status'] != '200':
            raise Exception(u"Invalid response %s.\n%s" % (resp['status'], content))
        items = json.loads(content)
        end = timer()
        print "Execution time: " + str(end - start)
        return items


