# coding=UTF-8
import logging

import facebook
from tornado import auth
from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections
from commons.errors import ApiError


class FacebookApi(ApiHandler, auth.FacebookGraphMixin, web.RequestHandler):
    @decorators.authenticated
    @web.asynchronous
    async def get(self):

        user_doc = await self.db[collections.USERS].find_one(
            {fields.MONGO_ID: self.getUserId()})

        if fields.FACEBOOK not in user_doc:
            raise ApiError('Użytkownik nie ma konta połączonego z Facebook.')

        token = user_doc[fields.FACEBOOK][fields.FACEBOOK_ACCESS_TOKEN]

        graph = facebook.GraphAPI(access_token=token, version='2.6')

        # Get all of the authenticated user's friends
        friends = graph.get_connections(id='me', connection_name='friends')
        all_friends = list()
        while friends['data']:
            try:
                for friend in friends['data']:
                    all_friends.append(friend['name'])
                    friends = facebook.requests.get("/after={}".format(friends['paging']['cursors']['after']))
            except Exception as ex:
                logging.error("Key Error" + ex.message)

        logging.debug(all_friends)
        logging.debug(friends)

    @web.asynchronous
    def _save_user_profile(self, user):
        if not user:
            raise web.HTTPError(log_message="Facebook authentication failed.")
        else:
            # while user['cursor']
            logging.info(user)
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
