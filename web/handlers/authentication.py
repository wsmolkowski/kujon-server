# coding=UTF-8

import logging
from datetime import datetime

import json
import motor
import oauth2 as oauth
import tornado.auth
import tornado.gen
import tornado.web
from bson import json_util

from base import BaseHandler
from commons import constants, settings
from crawler import job_factory

COOKIE_FIELDS = ('id', constants.USOS_URL, constants.ACCESS_TOKEN_KEY, constants.ACCESS_TOKEN_SECRET, constants.USOS_ID,
                 constants.USOS_PAIRED)


class LoginHandler(BaseHandler):
    def get(self):
        data = self.template_data()
        self.render("login.html", **data)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        access_token_key = self.get_argument("inputAccessTokenKey")
        access_token_secret = self.get_argument("inputAccessTokenSecret")

        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.ACCESS_TOKEN_SECRET: access_token_secret,
             constants.ACCESS_TOKEN_KEY: access_token_key},
            constants.USER_PRESENT_KEYS)
        if user_doc:
            user_doc[constants.USER_ID] = str(user_doc[constants.MONGO_ID])
            user_doc.pop(constants.MONGO_ID)

            self.set_secure_cookie(constants.USER_SECURE_COOKIE,
                                   tornado.escape.json_encode(json_util.dumps(user_doc)),
                                   constants.COOKIE_EXPIRES_DAYS)
            self.redirect('/')
        else:
            data = self.template_data()
            data[constants.ALERT_MESSAGE] = u"login authentication failed for {0} and {1}".format(access_token_key,
                                                                                                  access_token_secret)
            self.render("login.html", **data)


class FacebookOAuth2LoginHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=settings.DEPLOY_WEB + '/authentication/facebook',
                client_id=self.settings['facebook_oauth']['key'],
                client_secret=self.settings['facebook_oauth']['secret'],
                code=self.get_argument('code'),
                extra_fields={'email', 'id'})

            user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
                {'email': access['email']},
                COOKIE_FIELDS)

            if not user_doc:
                user = dict()
                user[constants.USER_TYPE] = 'facebook'
                user[constants.USER_NAME] = access['name']
                user[constants.USER_PICTURE] = access['picture']['data']['url']
                user[constants.USER_EMAIL] = access['email']
                user[constants.USOS_PAIRED] = False
                user[constants.USER_CREATED] = datetime.now()
                user[constants.USOS_URL] = None

                user_doc = yield motor.Op(self.db.users.insert, user)
                logging.debug(u"saved new user in database: {0}".format(user_doc))

                user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_doc},
                                                                              COOKIE_FIELDS)
            self.set_secure_cookie(constants.USER_SECURE_COOKIE,
                                   tornado.escape.json_encode(json_util.dumps(user_doc)),
                                   constants.COOKIE_EXPIRES_DAYS)

            self.redirect("/")
        else:
            yield self.authorize_redirect(
                redirect_uri=settings.DEPLOY_WEB + '/authentication/facebook',
                client_id=self.settings['facebook_oauth']['key'],
                scope=['public_profile', 'email', 'user_friends'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class GoogleOAuth2LoginHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=settings.DEPLOY_WEB + '/authentication/google',
                code=self.get_argument('code'))
            user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])

            user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
                {'email': user['email']},
                COOKIE_FIELDS)

            if not user_doc:
                userToInsert = dict()
                userToInsert[constants.USER_TYPE] = 'google'
                userToInsert[constants.USER_NAME] = user['name']
                userToInsert[constants.USER_PICTURE] = user['picture']
                userToInsert[constants.USER_EMAIL] = user['email']
                userToInsert[constants.USOS_PAIRED] = False
                userToInsert[constants.USER_CREATED] = datetime.now()
                userToInsert[constants.USOS_URL] = None

                user_doc = yield motor.Op(self.db.users.insert, userToInsert)
                logging.debug(u"saved new user in database: {0}".format(user_doc))

                user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_doc},
                                                                              COOKIE_FIELDS)
            self.set_secure_cookie(constants.USER_SECURE_COOKIE,
                                   tornado.escape.json_encode(json_util.dumps(user_doc)),
                                   constants.COOKIE_EXPIRES_DAYS)

            self.redirect("/")

        else:
            yield self.authorize_redirect(
                redirect_uri=settings.DEPLOY_WEB + '/authentication/google',
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(constants.USER_SECURE_COOKIE)
        self.redirect("/")


class CreateUserHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        data = json.loads(self.request.body)

        usos_doc = yield self.get_usos(constants.USOS_ID, data[constants.USOS_ID])

        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: self.get_current_user()[constants.MONGO_ID]})

        if not user_doc:
            self.error("Użytkownik musi posiadać konto.")
            return

        if user_doc[constants.USOS_URL]:
            data = self.template_data()
            data[constants.ALERT_MESSAGE] = "user: already register for usos".format(user_doc[constants.USOS_ID])

            self.error(data)
            return

        consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

        request_token_url = "{0}services/oauth/request_token?{1}&oauth_callback={2}".format(
            usos_doc[constants.USOS_URL], 'scopes=studies|offline_access|student_exams|grades', settings.CALLBACK_URL )

        client = oauth.Client(consumer, **self.oauth_parameters)
        resp, content = client.request(request_token_url)
        if resp['status'] != '200':
            raise Exception("Invalid response %s:\n%s" % (resp['status'], content))

        request_token = self.get_token(content)

        # updating to db user access_token_key & access_token_secret
        access_token_key = request_token.key
        access_token_secret = request_token.secret

        update = user_doc
        update[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        update[constants.USOS_URL] = usos_doc[constants.USOS_URL]
        # update[constants.MOBILE_ID] = mobile_id
        update[constants.ACCESS_TOKEN_SECRET] = access_token_secret
        update[constants.ACCESS_TOKEN_KEY] = access_token_key
        update[constants.UPDATE_TIME] = datetime.now()

        user_doc = yield self.db[constants.COLLECTION_USERS].update({constants.MONGO_ID: user_doc[constants.MONGO_ID]}, update)
        logging.debug("updated user with usos base info: %r", user_doc)

        authorize_url = usos_doc[constants.USOS_URL] + 'services/oauth/authorize'
        url_redirect = "%s?oauth_token=%s" % (authorize_url, request_token.key)

        self.success({'redirect': url_redirect})

        #self.redirect(url_redirect)


class VerifyHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        oauth_token_key = self.get_argument("oauth_token")
        oauth_verifier = self.get_argument("oauth_verifier")

        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({'id': self.get_current_user()['id']})

        template_data = self.template_data()

        if user_doc:

            usos_doc = yield self.db[constants.COLLECTION_USOSINSTANCES].find_one({constants.USOS_URL: user_doc[
                constants.USOS_URL]})
            usos_doc = self.aes.decrypt_usos(usos_doc)

            request_token = oauth.Token(user_doc[constants.ACCESS_TOKEN_KEY], user_doc[
                constants.ACCESS_TOKEN_SECRET])
            request_token.set_verifier(oauth_verifier)
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[
                constants.CONSUMER_SECRET])
            client = oauth.Client(consumer, request_token, **self.oauth_parameters)
            access_token_url = usos_doc[constants.USOS_URL] + 'services/oauth/access_token'
            esp, content = client.request(access_token_url, "GET")

            updated_user = dict()
            try:
                access_token = self.get_token(content)

                updated_user = user_doc
                updated_user[constants.USOS_PAIRED] = True
                updated_user[constants.ACCESS_TOKEN_SECRET] = access_token.secret
                updated_user[constants.ACCESS_TOKEN_KEY] = access_token.key
                updated_user[constants.UPDATE_TIME] = datetime.now()
                updated_user[constants.OAUTH_VERIFIER] = oauth_verifier

                user_doc_updated = yield self.db[constants.COLLECTION_USERS].update(
                    {constants.MONGO_ID: user_doc[constants.MONGO_ID]}, updated_user)

                template_data[constants.ALERT_MESSAGE] = "user_doc authenticated with mobile_id / username: {0}".format(
                    user_doc_updated)

                user_doc = yield self.db[constants.COLLECTION_USERS].find_one({'_id': self.get_current_user()['_id']},
                                                                              COOKIE_FIELDS)
                self.clear_cookie(constants.USER_SECURE_COOKIE)
                self.set_secure_cookie(constants.USER_SECURE_COOKIE,
                                       tornado.escape.json_encode(json_util.dumps(user_doc)),
                                       constants.COOKIE_EXPIRES_DAYS)

                # self.crawler.put_user(updated_user[constants.ID])

                self.redirect('/')
            except KeyError:
                template_data[constants.ALERT_MESSAGE] = "failed user_doc authenticate with {0} {1}".format(
                    updated_user[constants.ACCESS_TOKEN_SECRET], updated_user[
                        constants.ACCESS_TOKEN_KEY])

            self.redirect("/")
        else:
            template_data[
                constants.ALERT_MESSAGE] = "user_doc not found for given oauth_token_key:{0}, oauth_verifier: {1}".format(
                oauth_token_key, oauth_verifier)
            self.render("#create", **template_data)


class RegisterHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        usos_url = self.get_argument("usos").strip()

        usos_doc = yield self.db[constants.COLLECTION_USOSINSTANCES].find_one({constants.USOS_URL: usos_url})
        usos_doc = self.aes.decrypt_usos(usos_doc)

        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({'id': self.get_current_user()['_id']})

        if user_doc[constants.USOS_URL]:
            usoses = yield self.db.usosinstances.find().to_list(length=100)
            data = self.template_data()
            data[constants.ALERT_MESSAGE] = "user: already register for usos".format(usos_url)
            data["usoses"] = usoses

            self.write(data)
        else:
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

            request_token_url = "{0}services/oauth/request_token?{1}&oauth_callback={2}".format(
                usos_doc[constants.USOS_URL], 'scopes=studies|offline_access|student_exams|grades', settings.CALLBACK_URL )

            client = oauth.Client(consumer, **self.oauth_parameters)
            resp, content = client.request(request_token_url)
            if resp['status'] != '200':
                raise Exception("Invalid response %s:\n%s" % (resp['status'], content))

            request_token = self.get_token(content)

            # updating to db user access_token_key & access_token_secret
            access_token_key = request_token.key
            access_token_secret = request_token.secret

            update = user_doc
            update[constants.USOS_ID] = usos_doc[constants.USOS_ID]
            update[constants.USOS_URL] = usos_url
            # update[constants.MOBILE_ID] = mobile_id
            update[constants.ACCESS_TOKEN_SECRET] = access_token_secret
            update[constants.ACCESS_TOKEN_KEY] = access_token_key
            update[constants.UPDATE_TIME] = datetime.now()

            user_doc = yield self.db[constants.COLLECTION_USERS].update({constants.MONGO_ID: user_doc[constants.MONGO_ID]}, update)
            logging.debug(u"updated user with usos base info: {0}".format(user_doc))

            authorize_url = usos_url + 'services/oauth/authorize'
            url_redirect = "%s?oauth_token=%s" % (authorize_url, request_token.key)
            self.redirect(url_redirect)


class VerifyHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        # oauth_token_key = self.get_argument("oauth_token")
        oauth_verifier = self.get_argument("oauth_verifier")

        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: self.get_current_user()[constants.MONGO_ID]})

        if user_doc:
            usos_doc = yield self.db[constants.COLLECTION_USOSINSTANCES].find_one({constants.USOS_URL: user_doc[
                constants.USOS_URL]})
            usos_doc = self.aes.decrypt_usos(usos_doc)

            request_token = oauth.Token(user_doc[constants.ACCESS_TOKEN_KEY], user_doc[
                constants.ACCESS_TOKEN_SECRET])
            request_token.set_verifier(oauth_verifier)
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[
                constants.CONSUMER_SECRET])
            client = oauth.Client(consumer, request_token, **self.oauth_parameters)
            access_token_url = usos_doc[constants.USOS_URL] + 'services/oauth/access_token'
            esp, content = client.request(access_token_url, "GET")

            access_token = self.get_token(content)

            updated_user = user_doc
            updated_user[constants.USOS_PAIRED] = True
            updated_user[constants.ACCESS_TOKEN_SECRET] = access_token.secret
            updated_user[constants.ACCESS_TOKEN_KEY] = access_token.key
            updated_user[constants.UPDATE_TIME] = datetime.now()
            updated_user[constants.OAUTH_VERIFIER] = oauth_verifier

            user_doc_updated = yield self.db[constants.COLLECTION_USERS].update(
                {constants.MONGO_ID: user_doc[constants.MONGO_ID]}, updated_user)

            logging.debug('user usos veryfication ok - db updated with {0}'.format(user_doc_updated))

            user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
                {constants.MONGO_ID: self.get_current_user()[constants.MONGO_ID]}, COOKIE_FIELDS)

            self.clear_cookie(constants.USER_SECURE_COOKIE)
            self.set_secure_cookie(constants.USER_SECURE_COOKIE,
                                   tornado.escape.json_encode(json_util.dumps(user_doc)),
                                   constants.COOKIE_EXPIRES_DAYS)

            self.db[constants.COLLECTION_JOBS_QUEUE].insert(job_factory.initial_user_job(user_doc[constants.MONGO_ID]))

            self.redirect('/')
        else:
            self.redirect('/')


