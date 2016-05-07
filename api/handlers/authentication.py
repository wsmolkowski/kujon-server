# coding=UTF-8

import json
import logging
from datetime import datetime, timedelta

import oauth2 as oauth
import tornado.auth
import tornado.gen
import tornado.web

from base import BaseHandler
from commons import constants, settings, decorators
from crawler import job_factory


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(constants.KUJON_SECURE_COOKIE)
        self.redirect(settings.DEPLOY_WEB)


class ArchiveHandler(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        user_doc = yield self.get_current_user()
        if user_doc:
            yield self.archive_user(user_doc[constants.MONGO_ID])

        self.clear_cookie(constants.KUJON_SECURE_COOKIE)
        self.redirect(settings.DEPLOY_WEB)


class FacebookOAuth2LoginHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=settings.DEPLOY_API + '/authentication/facebook',
                client_id=self.settings['facebook_oauth']['key'],
                client_secret=self.settings['facebook_oauth']['secret'],
                code=self.get_argument('code'),
                extra_fields={'email', 'id'})

            user_doc = yield self.find_user_email(access['email'])

            if not user_doc:
                user = dict()
                user[constants.USER_TYPE] = 'facebook'
                user[constants.USER_NAME] = access['name']
                user[constants.USER_PICTURE] = access['picture']['data']['url']
                user[constants.USER_EMAIL] = access['email']
                user[constants.USOS_PAIRED] = False
                user[constants.USER_CREATED] = datetime.now()

                yield self.insert_user(user)

                user_doc = yield self.cookie_user_id(user_doc[constants.MONGO_ID])

            self.reset_user_cookie(user_doc)

            self.redirect(settings.DEPLOY_WEB + '/#home')
        else:
            yield self.authorize_redirect(
                redirect_uri=settings.DEPLOY_API + '/authentication/facebook',
                client_id=self.settings['facebook_oauth']['key'],
                scope=['public_profile', 'email', 'user_friends', 'user_managed_groups', 'user_birthday',
                       'user_education_history', 'read_custom_friendlists'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class GoogleOAuth2LoginHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        if self.get_argument('error', False):
            logging.error('Error while Google+ authentication. Redirecting to home.')
            self.redirect(settings.DEPLOY_WEB + '/')
            return

        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=settings.DEPLOY_API + '/authentication/google',
                code=self.get_argument('code'))
            user = yield self.oauth2_request(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                access_token=access['access_token'])

            user_doc = yield self.find_user_email(user['email'])

            if not user_doc:
                insert_doc = dict()
                insert_doc[constants.USER_TYPE] = 'google'
                insert_doc[constants.USER_NAME] = user['name']
                insert_doc[constants.USER_PICTURE] = user['picture']
                insert_doc[constants.USER_EMAIL] = user['email']
                insert_doc[constants.USOS_PAIRED] = False
                insert_doc[constants.USER_CREATED] = datetime.now()

                insert_doc[constants.GAUTH_ACCESS_TOKEN] = access['access_token']
                insert_doc[constants.GAUTH_EXPIRES_IN] = datetime.now() + timedelta(seconds=access['expires_in'])
                insert_doc[constants.GAUTH_ID_TOKEN] = access['id_token']
                insert_doc[constants.GAUTH_TOKEN_TYPE] = access['token_type']

                user_doc = yield self.insert_user(insert_doc)
                user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
                    {constants.MONGO_ID: user_doc}, self._COOKIE_FIELDS)
                user_doc = yield self.cookie_user_id(user_doc[constants.MONGO_ID])

            else:
                user_doc[constants.GAUTH_ACCESS_TOKEN] = access['access_token']
                user_doc[constants.GAUTH_EXPIRES_IN] = datetime.now() + timedelta(seconds=access['expires_in'])
                user_doc[constants.GAUTH_ID_TOKEN] = access['id_token']
                user_doc[constants.GAUTH_TOKEN_TYPE] = access['token_type']
                user_doc[constants.UPDATE_TIME] = datetime.now()

                yield self.update_user(user_doc[constants.MONGO_ID], user_doc)
                user_doc = yield self.cookie_user_id(user_doc[constants.MONGO_ID])

            self.reset_user_cookie(user_doc)
            self.redirect(settings.DEPLOY_WEB + '/#home')

        else:
            yield self.authorize_redirect(
                redirect_uri=settings.DEPLOY_API + '/authentication/google',
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class UsosRegisterHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        data = json.loads(self.request.body)

        usos_doc = yield self.get_usos(constants.USOS_ID, data[constants.USOS_ID])

        user_doc = yield self.find_user()

        if not user_doc:
            self.error('Użytkownik musi posiadać konto. Prośba o zalogowanie.')
            return

        if constants.USOS_PAIRED in user_doc and user_doc[constants.USOS_PAIRED]:
            self.error('Użytkownik jest już zarejestrowany w {0}.'.format(user_doc[constants.USOS_ID]))
            return

        try:
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

            request_token_url = '{0}services/oauth/request_token?{1}&oauth_callback={2}'.format(
                usos_doc[constants.USOS_URL], 'scopes=studies|offline_access|student_exams|grades',
                settings.CALLBACK_URL)

            # is USOS have disabled SSL validation
            if constants.DISABLE_SSL_CERT_VALIDATION in usos_doc and constants.DISABLE_SSL_CERT_VALIDATION:
                params = self.oauth_parameters
                params[constants.DISABLE_SSL_CERT_VALIDATION] = True
                client = oauth.Client(consumer, **params)
            else:
                client = oauth.Client(consumer, **self.oauth_parameters)

            resp, content = client.request(request_token_url)
        except Exception, ex:
            msg = 'Wystąpił problem z połączeniem z serwerem USOS {0}'.format(ex.message)
            logging.exception(msg)
            self.error(msg)
            return

        if 'status' not in resp or resp['status'] != '200':
            self.error('Invalid USOS response %s:\n%s' % (resp['status'], content))
            return

        request_token = self.get_token(content)

        # updating to db user access_token_key & access_token_secret
        access_token_key = request_token.key
        access_token_secret = request_token.secret

        update = user_doc
        update[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        update[constants.ACCESS_TOKEN_SECRET] = access_token_secret
        update[constants.ACCESS_TOKEN_KEY] = access_token_key
        update[constants.UPDATE_TIME] = datetime.now()

        yield self.update_user(user_doc[constants.MONGO_ID], update)

        authorize_url = usos_doc[constants.USOS_URL] + 'services/oauth/authorize'
        url_redirect = '%s?oauth_token=%s' % (authorize_url, request_token.key)

        self.success({'redirect': url_redirect})


class UsosVerificationHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        # oauth_token_key = self.get_argument('oauth_token')
        user_doc = yield self.find_user()

        if self.get_argument('error', False):
            updated_user = user_doc
            updated_user[constants.USOS_PAIRED] = False
            updated_user[constants.ACCESS_TOKEN_SECRET] = None
            updated_user[constants.ACCESS_TOKEN_KEY] = None
            updated_user[constants.UPDATE_TIME] = datetime.now()
            updated_user[constants.OAUTH_VERIFIER] = None

            yield self.update_user(user_doc[constants.MONGO_ID], updated_user)

            user_doc = yield self.cookie_user_id(user_doc[constants.MONGO_ID])

            self.reset_user_cookie(user_doc)
            self.redirect(settings.DEPLOY_WEB + '/#register')
            return

        oauth_verifier = self.get_argument('oauth_verifier')

        if user_doc:
            usos_doc = yield self.get_usos(constants.USOS_ID, user_doc[constants.USOS_ID])

            request_token = oauth.Token(user_doc[constants.ACCESS_TOKEN_KEY], user_doc[
                constants.ACCESS_TOKEN_SECRET])
            request_token.set_verifier(oauth_verifier)
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

            # is USOS have disabled SSL validation
            if constants.DISABLE_SSL_CERT_VALIDATION in usos_doc and constants.DISABLE_SSL_CERT_VALIDATION:
                params = self.oauth_parameters
                params[constants.DISABLE_SSL_CERT_VALIDATION] = True
                client = oauth.Client(consumer, request_token,  **params)
            else:
                client = oauth.Client(consumer, request_token, **self.oauth_parameters)

            access_token_url = '{0}{1}'.format(usos_doc[constants.USOS_URL], 'services/oauth/access_token')
            esp, content = client.request(access_token_url, 'GET')
            if esp.status != 200:
                self.error('Bład podczas oauth USOS')
                return

            access_token = self.get_token(content)

            updated_user = user_doc
            updated_user[constants.USOS_PAIRED] = True
            updated_user[constants.ACCESS_TOKEN_SECRET] = access_token.secret
            updated_user[constants.ACCESS_TOKEN_KEY] = access_token.key
            updated_user[constants.UPDATE_TIME] = datetime.now()
            updated_user[constants.OAUTH_VERIFIER] = oauth_verifier

            yield self.update_user(user_doc[constants.MONGO_ID], updated_user)

            user_doc = yield self.cookie_user_id(updated_user[constants.MONGO_ID])

            self.reset_user_cookie(user_doc)

            self.db[constants.COLLECTION_JOBS_QUEUE].insert(job_factory.initial_user_job(user_doc[constants.MONGO_ID]))

            yield self.email_registration()

            self.redirect(settings.DEPLOY_WEB + '/#home')
        else:
            self.redirect(settings.DEPLOY_WEB)


class MobiAuthHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        email = self.get_argument('email', default=None, strip=True)
        token = self.get_argument('token', default=None, strip=True)
        usos_id = self.get_argument('usos_id', default=None, strip=True)

        if not email or not token or not usos_id:
            self.error('One of the provided parameters is incorrect.')
            return

        usos_doc = yield self.get_usos(constants.USOS_ID, usos_id)

        try:
            http_client = self.get_auth_http_client()
            tokeninfo = yield http_client.fetch('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=' + token)
            if tokeninfo.code != 200 or tokeninfo.reason != 'OK':
                raise Exception(
                    'Token validation {0} status {1} body {2}'.format(tokeninfo.reason, tokeninfo.code, tokeninfo.body))
            yield self.insert_token(json.loads(tokeninfo.body))
        except (Exception, tornado.web.HTTPError), ex:
            self.error('Google token verification failure. {0}'.format(ex.message))
            return

        user_doc = yield self.user_exists(email, usos_id)
        if user_doc:
            self.error('User already registered.')
            return

        try:
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

            request_token_url = '{0}services/oauth/request_token?{1}&oauth_callback={2}'.format(
                usos_doc[constants.USOS_URL], 'scopes=studies|offline_access|student_exams|grades',
                settings.CALLBACK_MOBI_URL + '?token=' + token)

            # is USOS have disabled SSL validation
            if constants.DISABLE_SSL_CERT_VALIDATION in usos_doc and constants.DISABLE_SSL_CERT_VALIDATION:
                params = self.oauth_parameters
                params[constants.DISABLE_SSL_CERT_VALIDATION] = True
                client = oauth.Client(consumer, **params)
            else:
                client = oauth.Client(consumer, **self.oauth_parameters)

            resp, content = client.request(request_token_url)
        except Exception, ex:
            msg = 'Wystąpił problem z połączeniem z serwerem USOS {0}'.format(ex.message)
            logging.exception(msg)
            self.error(msg)
            return

        if 'status' not in resp or resp['status'] != '200':
            self.error('Invalid USOS response %s:\n%s' % (resp['status'], content))
            return

        request_token = self.get_token(content)

        # updating to db user access_token_key & access_token_secret
        access_token_key = request_token.key
        access_token_secret = request_token.secret

        # update = user_doc
        if not user_doc:
            new_user = True
            user_doc = dict()
            user_doc[constants.USER_EMAIL] = email
        else:
            new_user = False

        update = user_doc
        update[constants.MOBI_TOKEN] = token
        update[constants.USER_EMAIL] = email
        update[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        update[constants.ACCESS_TOKEN_SECRET] = access_token_secret
        update[constants.ACCESS_TOKEN_KEY] = access_token_key
        update[constants.CREATED_TIME] = datetime.now()
        update[constants.UPDATE_TIME] = datetime.now()

        if new_user:
            yield self.insert_user(update)
        else:
            yield self.update_user_email(email, update)

        authorize_url = usos_doc[constants.USOS_URL] + 'services/oauth/authorize'
        url_redirect = '%s?oauth_token=%s' % (authorize_url, request_token.key)
        self.redirect(url_redirect)


class UsosMobiVerificationHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        # oauth_token_key = self.get_argument('oauth_token')
        oauth_verifier = self.get_argument('oauth_verifier')
        token = self.get_argument('token')

        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.MOBI_TOKEN: token})

        if self.get_argument('error', False):
            updated_user = user_doc
            updated_user[constants.USOS_PAIRED] = False
            updated_user[constants.ACCESS_TOKEN_SECRET] = None
            updated_user[constants.ACCESS_TOKEN_KEY] = None
            updated_user[constants.UPDATE_TIME] = datetime.now()
            updated_user[constants.OAUTH_VERIFIER] = None

            yield self.update_user(user_doc[constants.MONGO_ID], updated_user)

            self.reset_user_cookie()
            self.redirect(settings.DEPLOY_WEB + '/#register')
            return

        if user_doc:
            usos_doc = yield self.get_usos(constants.USOS_ID, user_doc[constants.USOS_ID])

            request_token = oauth.Token(user_doc[constants.ACCESS_TOKEN_KEY], user_doc[
                constants.ACCESS_TOKEN_SECRET])
            request_token.set_verifier(oauth_verifier)
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

            # is USOS have disabled SSL validation
            if constants.DISABLE_SSL_CERT_VALIDATION in usos_doc and constants.DISABLE_SSL_CERT_VALIDATION:
                params = self.oauth_parameters
                params[constants.DISABLE_SSL_CERT_VALIDATION] = True
                client = oauth.Client(consumer, request_token, **params)
            else:
                client = oauth.Client(consumer, request_token, **self.oauth_parameters)

            access_token_url = '{0}{1}'.format(usos_doc[constants.USOS_URL], 'services/oauth/access_token')
            esp, content = client.request(access_token_url, 'GET')
            if esp['status'] != '200':
                self.error('Bład podczas oauth USOS')

            access_token = self.get_token(content)

            updated_user = user_doc
            updated_user[constants.USOS_PAIRED] = True
            updated_user[constants.ACCESS_TOKEN_SECRET] = access_token.secret
            updated_user[constants.ACCESS_TOKEN_KEY] = access_token.key
            updated_user[constants.UPDATE_TIME] = datetime.now()
            updated_user[constants.OAUTH_VERIFIER] = oauth_verifier

            yield self.update_user(user_doc[constants.MONGO_ID], updated_user)

            self.db[constants.COLLECTION_JOBS_QUEUE].insert(job_factory.initial_user_job(user_doc[constants.MONGO_ID]))

            self.success('Usos paired successfully.')
        else:
            self.error('Usos paired failed.')
