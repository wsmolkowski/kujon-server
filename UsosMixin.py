from __future__ import absolute_import, division, print_function, with_statement

import functools

from tornado.concurrent import return_future
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from tornado import escape


try:
    import urlparse  # py2
except ImportError:
    import urllib.parse as urlparse  # py3

try:
    import urllib.parse as urllib_parse  # py3
except ImportError:
    import urllib as urllib_parse  # py2

from tornado.auth import OAuthMixin
from tornado.auth import _auth_return_future, AuthError


class UsosMixin2(OAuthMixin):
    _OAUTH_REQUEST_TOKEN_URL = "https://usosapps.uw.edu.pl/services/oauth/request_token"
    _OAUTH_ACCESS_TOKEN_URL = "https://usosapps.uw.edu.pl/services/oauth/access_token"
    _OAUTH_AUTHORIZE_URL = "https://usosapps.uw.edu.pl/services/oauth/authorize"
    _OAUTH_AUTHENTICATE_URL = "https://usosapps.uw.edu.pl/oauth/authenticate"   #TODO
    _OAUTH_NO_CALLBACKS = True
    _USOS_BASE_URL = "http://usosapps.uw.edu.pl/"   #developers/api

    def get_auth_http_client(self):
        """Returns the `.AsyncHTTPClient` instance to be used for auth requests.

        May be overridden by subclasses to use an HTTP client other than
        the default.
        """
        return AsyncHTTPClient()

    @return_future
    def authenticate_redirect(self, callback_uri=None, callback=None):
        """Just like `~OAuthMixin.authorize_redirect`, but
        auto-redirects if authorized.

        This is generally the right interface to use if you are using
        Twitter for single-sign on.

        .. versionchanged:: 3.1
           Now returns a `.Future` and takes an optional callback, for
           compatibility with `.gen.coroutine`.
        """
        http = self.get_auth_http_client()
        http.fetch(self._oauth_request_token_url(callback_uri=callback_uri),
                   functools.partial(
                       self._on_request_token, self._OAUTH_AUTHENTICATE_URL,
                       None, callback),
                   validate_cert=False)

    @_auth_return_future
    def twitter_request(self, path, callback=None, access_token=None,
                        post_args=None, **args):
        """Fetches the given API path, e.g., ``statuses/user_timeline/btaylor``

        The path should not include the format or API version number.
        (we automatically use JSON format and API version 1).

        If the request is a POST, ``post_args`` should be provided. Query
        string arguments should be given as keyword arguments.

        All the Twitter methods are documented at http://dev.twitter.com/

        Many methods require an OAuth access token which you can
        obtain through `~OAuthMixin.authorize_redirect` and
        `~OAuthMixin.get_authenticated_user`. The user returned through that
        process includes an 'access_token' attribute that can be used
        to make authenticated requests via this method. Example
        usage:

        .. testcode::

            class MainHandler(tornado.web.RequestHandler,
                              tornado.auth.TwitterMixin):
                @tornado.web.authenticated
                @tornado.gen.coroutine
                def get(self):
                    new_entry = yield self.twitter_request(
                        "/statuses/update",
                        post_args={"status": "Testing Tornado Web Server"},
                        access_token=self.current_user["access_token"])
                    if not new_entry:
                        # Call failed; perhaps missing permission?
                        yield self.authorize_redirect()
                        return
                    self.finish("Posted a message!")

        .. testoutput::
           :hide:

        """
        if path.startswith('http:') or path.startswith('https:'):
            # Raw urls are useful for e.g. search which doesn't follow the
            # usual pattern: http://search.twitter.com/search.json
            url = path
        else:
            url = self._USOS_BASE_URL + path + ".json"
        # Add the OAuth resource request signature if we have credentials
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            method = "POST" if post_args is not None else "GET"
            oauth = self._oauth_request_parameters(
                url, access_token, all_args, method=method)
            args.update(oauth)
        if args:
            url += "?" + urllib_parse.urlencode(args)
        http = self.get_auth_http_client()
        http_callback = functools.partial(self._on_twitter_request, callback)
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib_parse.urlencode(post_args),
                       callback=http_callback, validate_cert=False)
        else:
            http.fetch(url, callback=http_callback, validate_cert=False)

    def _on_twitter_request(self, future, response):
        if response.error:
            future.set_exception(AuthError(
                "Error response %s fetching %s" % (response.error,
                                                   response.request.url)))
            return
        future.set_result(escape.json_decode(response.body))

    def _oauth_consumer_token(self):
        #self.require_setting("consumer_key", "Consumer Key")
        #self.require_setting("consumer_secret", "Consumer Secret")
        return dict(
            key="vxSehcx4RCA8m4kgjRhY",
            secret="T7eJsSJHSxKCshK9jrdNbNy3XCG3UXzQuYKL2VbJ")

    @gen.coroutine
    def _oauth_get_user_future(self, access_token):
        user = yield self.twitter_request(
            "/account/verify_credentials",
            access_token=access_token)
        if user:
            user["username"] = user["screen_name"]
        raise gen.Return(user)


class UsosMixin(OAuthMixin):
    _OAUTH_AUTHORIZE_URL = "https://usosapps.uw.edu.pl/services/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://usosapps.uw.edu.pl/services/oauth/access_token"
    _OAUTH_REQUEST_TOKEN_URL = "https://usosapps.uw.edu.pl/services/oauth/request_token"
    _OAUTH_VERSION = "1.0a"
    _OAUTH_NO_CALLBACKS = False

    @gen.coroutine
    def _oauth_get_user_future(self, access_token, callback):

        raise gen.Return("asdasd")
        '''
        user = yield self.twitter_request(
            "/account/verify_credentials",
            access_token=access_token)
        if user:
            user["username"] = user["screen_name"]
        raise gen.Return(user)
        '''

    def _oauth_consumer_token(self):
        return dict(
            key="vxSehcx4RCA8m4kgjRhY",
            secret="T7eJsSJHSxKCshK9jrdNbNy3XCG3UXzQuYKL2VbJ")

