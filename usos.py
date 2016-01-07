import json
import pprint
from datetime import datetime
from timeit import default_timer as timer

import oauth2 as oauth
import settings

# Access Token to use. If left blank, then user authorization process will follow.
access_token_key = '3ShYQv8LyvgeXthKJzmJ'
access_token_secret = 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'


# End of settings. Program starts here.


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


def main():
    # user_id = handlers.UserHandler()
    pp = pprint.PrettyPrinter(indent=4)


    #
    access_token_key = 'uXLyCGpp5zfHPH4z4brg'
    access_token_secret = 'VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy'

    updater = USOSUpdater(3, access_token_key, access_token_secret)


    print "plan dnia dzisieszego"
    url="services/tt/student?start=" + str(datetime.now().date()) + "&days=1"
    pp.pprint(updater.request(url))

    print "proba wyciagniacia info o userze"
    url = "services/users/user?fields=id|first_name|last_name|student_status|sex|email|student_programmes|student_number|has_email|titles"
    pp.pprint(updater.request(url))

    print "get courses_editions"
    url = "services/courses/user"
    pp.pprint(updater.request(url))

    print "get grades for given courses_editions"
    url = "services/grades/course_edition?course_id=E-2IZ2-1004-s3&term_id=2014/15-1"
    pp.pprint(updater.request(url))



if __name__ == "__main__":
    main()
