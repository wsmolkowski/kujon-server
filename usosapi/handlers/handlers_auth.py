import logging
from datetime import datetime

import motor
import tornado.web
from bson import json_util

import usosapi.oauth2 as oauth
import usosapi.settings
from handlers_api import BaseHandler
from usosapi import constants


class LoginHandler(BaseHandler):
    def get(self):
        data = self.template_data()
        self.render("login.html", **data)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        access_token_key = self.get_argument("inputAccessTokenKey")
        access_token_secret = self.get_argument("inputAccessTokenSecret")
        next_page = self.get_argument(constants.NEXT_PAGE, "/")

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: access_token_key},
                                                constants.USER_PRESENT_KEYS)
        if user_doc:
            self.set_secure_cookie(constants.USER_SECURE_COOKIE,
                                   tornado.escape.json_encode(json_util.dumps(user_doc)),
                                   constants.COOKIE_EXPIRES_DAYS)
            self.redirect(next_page)
        else:
            data = self.template_data()
            data[constants.ALERT_MESSAGE] = "login authentication failed for {0} and {1}".format(access_token_key,
                                                                                                 access_token_secret)
            self.render("login.html", **data)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(constants.USER_SECURE_COOKIE)
        self.redirect("/")


class CreateUserHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        usoses = yield self.db.usosinstances.find().to_list(length=100)
        data = self.template_data()
        data['usoses'] = usoses

        self.render("create.html", **data)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        mobile_id = self.get_argument(constants.MOBILE_ID).strip()
        usos_url = self.get_argument("usos").strip()

        usos_doc = yield self.db.usosinstances.find_one({constants.URL: usos_url})

        # try to find user in db
        user = yield self.db.users.find_one({constants.MOBILE_ID: mobile_id, constants.USOS_ID: usos_doc[
            constants.USOS_ID]})
        if user:
            usoses = yield self.db.usosinstances.find().to_list(length=100)
            data = self.template_data()
            data[constants.ALERT_MESSAGE] = "mobile_id / username: {0} already exists".format(mobile_id)
            data["usoses"] = usoses

            self.render("create.html", **data)
        else:
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[
                constants.CONSUMER_SECRET])
            request_token_url = usos_doc[
                                    constants.URL] + 'services/oauth/request_token?scopes=studies|offline_access'
            client = oauth.Client(consumer, proxy_info=self.get_proxy())
            resp, content = client.request(request_token_url, "GET", callback_url=usosapi.settings.CALLBACK_URL)
            if resp['status'] != '200':
                raise Exception("Invalid response %s:\n%s" % (resp['status'], content))

            request_token = self.get_token(content)

            # updating to db user access_token_key & access_token_secret
            access_token_key = request_token.key
            access_token_secret = request_token.secret

            result = dict()
            result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
            result[constants.MOBILE_ID] = mobile_id
            result[constants.ACCESS_TOKEN_SECRET] = access_token_secret
            result[constants.ACCESS_TOKEN_KEY] = access_token_key
            result[constants.CREATED_TIME] = datetime.now()

            user_doc = yield motor.Op(self.db.users.insert, result)
            logging.info("saved new user in database: {0}".format(user_doc))

            authorize_url = usos_url + 'services/oauth/authorize'
            url_redirect = "%s?oauth_token=%s" % (authorize_url, request_token.key)
            self.redirect(url_redirect)


class VerifyHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        oauth_token_key = self.get_argument("oauth_token")
        oauth_verifier = self.get_argument("oauth_verifier")

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_KEY: oauth_token_key})

        data = self.template_data()

        if user_doc:
            usos_doc = yield self.db.usosinstances.find_one({constants.USOS_ID: user_doc[
                constants.USOS_ID]})

            request_token = oauth.Token(user_doc[constants.ACCESS_TOKEN_KEY], user_doc[
                constants.ACCESS_TOKEN_SECRET])
            request_token.set_verifier(oauth_verifier)
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[
                constants.CONSUMER_SECRET])
            client = oauth.Client(consumer, request_token, proxy_info=self.get_proxy())
            access_token_url = usos_doc[constants.URL] + 'services/oauth/access_token'
            esp, content = client.request(access_token_url, "GET")

            try:
                access_token = self.get_token(content)

                updated_user = dict()
                updated_user[constants.USOS_ID] = user_doc[constants.USOS_ID]
                updated_user[constants.MOBILE_ID] = user_doc[constants.MOBILE_ID]
                updated_user[constants.USOS_ID] = user_doc[constants.USOS_ID]
                updated_user[constants.ACCESS_TOKEN_SECRET] = access_token.secret
                updated_user[constants.ACCESS_TOKEN_KEY] = access_token.key
                updated_user[constants.CREATED_TIME] = datetime.now()
                updated_user[constants.OAUTH_VERIFIER] = oauth_verifier

                user_doc_updated = yield self.db.users.update({constants.ID: user_doc[constants.ID]}, updated_user)

                data[constants.ALERT_MESSAGE] = "user_doc authenticated with mobile_id / username: {0}".format(
                    user_doc_updated)

                # fetch user again to get actual id
                user_id = yield self.db.users.find_one({}, {constants.ACCESS_TOKEN_KEY: oauth_token_key})

                self.crowler.put_user(user_id[constants.ID])

            except KeyError:
                data[constants.ALERT_MESSAGE] = "failed user_doc authenticate with {0} {1}".format(
                        updated_user[constants.ACCESS_TOKEN_SECRET], updated_user[
                            constants.ACCESS_TOKEN_KEY])

            self.render("login.html", **data)
        else:

            data[
                constants.ALERT_MESSAGE] = "user_doc not found for given oauth_token_key:{0}, oauth_verifier: {1}".format(
                oauth_token_key, oauth_verifier)
            self.render("/authorization/create", **data)
