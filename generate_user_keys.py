
from Netflix import *
import settings

def getAuth(netflix):
    netflix.user = NetflixUser(settings.USER,netflix)
    
    if settings.USER['request']['key'] and not settings.USER['access']['key']:
        tok = netflix.user.getAccessToken( settings.USER['request'] )
        print "now put this key / secret in settings.USER.access so you don't have to re-authorize again:\n 'key': '%s',\n 'secret': '%s'\n" % (tok.key, tok.secret)
        settings.USER['access']['key'] = tok.key
        settings.USER['access']['secret'] = tok.secret
        sys.exit(1)

    elif not settings.USER['access']['key']:
        (tok, url) = netflix.user.getRequestToken()
        print "Authorize user access here: %s" % url
        print "and then put this key / secret in settings.USER.request:\n 'key': '%s',\n 'secret': '%s'\n" % (tok.key, tok.secret)
        print "and run again."
        sys.exit(1)

    else:
        print "Everything is in its place. You all good."
        sys.exit(0)

if __name__ == "__main__":
    netflix = NetflixClient(settings.APP_NAME, settings.API_KEY, settings.API_SECRET, settings.CALLBACK)
    getAuth(netflix)
