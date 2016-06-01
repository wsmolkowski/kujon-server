# coding=UTF-8

import facebook
import tornado.gen
import tornado.web
from bson.objectid import ObjectId

from base import ApiHandler
from commons import constants, decorators
from commons.errors import ApiError


class FacebookApi(ApiHandler, tornado.auth.FacebookGraphMixin, tornado.web.RequestHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: ObjectId(self.user_doc[constants.MONGO_ID])})

        self.friends = []
        if constants.FB not in user_doc:
            raise ApiError('Użytkownik nie ma konta połączonego z Facebook.')

        token = user_doc[constants.FB][constants.FB_ACCESS_TOKEN]

        # TODO: Make this fetch async rather than blocking
        graph = facebook.GraphAPI(access_token=token, version='2.6')
        profile = graph.get_object("me")

        # Get all of the authenticated user's friends
        friends = graph.get_connections(id='me', connection_name='friends')
        allfriends = list()
        while (friends['data']):
            try:
                for friend in friends['data']:
                    allfriends.append(friend['name'])
                friends = facebook.requests.get("/after={}".format(friends['paging']['cursors']['after']))
            except Exception, ex:
                print "Key Error" + ex.message
        print allfriends
        print friends

    @tornado.web.asynchronous
    def _save_user_profile(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Facebook authentication failed.")
        else:
            # while user['cursor']
            print user
            #     User.objects(email=user['email']).get()
            # except DoesNotExist, e:
            #     new_u = User()
            #     new_u.first_name = user['first_name']
            #     new_u.last_name = user['last_name']
            #     new_u.email = user['email']  # THIS IS WHAT YOU NEED
            #     new_u.username = user['username']
            #     new_u.gender = user['gender']
            #     new_u.locale = user['locale']
            #     new_u.fb_id = user['id']
            #     new_u.save()
            # else:
            #     # User exists
            #     pass
