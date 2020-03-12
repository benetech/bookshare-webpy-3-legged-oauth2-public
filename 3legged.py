import web
from requests_oauthlib import OAuth2Session
import json
import logging
import os

"""
3legged.py

A simple application which shows how to get a token from the Bookshare OAuth2 server and use it to 
make an API call to the Bookshare V2 API.
"""

# This will allow us to run even if this app is running without HTTPS, contrary to OAuth2 recommendations
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'True'

# Enabling debug will interfere with session handling
web.config.debug = False
logger = logging.getLogger()
logger.setLevel(logging.INFO)
render = web.template.render('templates/')

urls = (
    '/', 'index',
    '/callback', 'callback'
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore("sessions"), initializer={"count": 0})


class index:
    def GET(self):
        """
        Set up the main page
        """
        callback_url = web.ctx.home + "/callback"
        return render.start(callback_url)

    def POST(self):
        """
        Redirect user to Bookshare login
        """
        if 'token' in session and session['token'] is not None:
            logger.info("It looks like we already have a token from last time we could use to make the API call,"
                        " but we're going to get a new one anyway for demonstration purposes.")
            logger.info(session['token'])
        else:
            logger.info("No token in the session.")

        oauth_params = web.input()
        oauth_session = OAuth2Session(oauth_params['apiKey'], redirect_uri=oauth_params['redirectUri'],
                                      scope=oauth_params['scope'])

        # Anything relevant to our app that we need later, we need to store in session because we will be
        # redirecting the user's browser to another site, where we cannot write cookies.
        session['api_key'] = oauth_params['apiKey']
        session['redirect_uri'] = oauth_params['redirectUri']
        session['scope'] = oauth_params['scope']
        session['oauth2_server'] = oauth_params['oauth2Server']
        session['api_server'] = oauth_params['apiServer']
        auth_url = oauth_params['oauth2Server'] + "/oauth/authorize"
        authorization_url, state = oauth_session.authorization_url(auth_url, state=oauth_params['state'])
        session['state'] = state
        raise web.seeother(authorization_url)


class callback:
    def GET(self):
        """
        This is where Bookshare calls back with the code we need to fetch a token
        """

        callback_params = web.input()
        oauth_session = OAuth2Session(session['api_key'], redirect_uri=session['redirect_uri'],
                                      scope=session['scope'])
        token_response = fetch_token(oauth_session, session['oauth2_server'])
        logging.info(token_response)

        # Finally, make a call to the Bookshare API using our token.
        api_url = session['api_server'] + "/me"
        params = {'api_key': session['api_key']}
        api_response = oauth_session.get(api_url, params=params)
        logger.info("Request to Bookshare: " + api_response.url)
        logger.info("Headers sent to Bookshare: " + str(api_response.headers))
        json_response = json.loads(api_response.content)
        logging.info(api_response.content)

        return render.callback(callback_params, session, token_response, json_response)


def fetch_token(oauth_session, auth_server):
    """
    Get a code from the token
    :param oauth_session: OAuth2 session
    :param auth_server: URL of OAuth2 server
    :return:
    """
    if 'token' in session:
        del session['token']
    try:
        token_endpoint = auth_server + "/oauth/token"
        incoming_url = web.ctx.home + web.ctx.fullpath
        token = oauth_session.fetch_token(token_url=token_endpoint, authorization_response=incoming_url)
        session['token'] = token
        return token
    except Exception as e:
        logger.error("Can't get OAuth2 Token for callback " + incoming_url)
        logger.error(str(e))


if __name__ == "__main__":
    app.run()
