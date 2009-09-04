"""
Developer resources on Netflix:
    http://developer.netflix.com/docs/REST_API_Conventions#0_37461

Netflix.py comes from pyflix
    http://code.google.com/p/pyflix/
    (some bugs fixed and submitted to google code issues)

"""

from Netflix import *
import time
import datetime
import settings

def _movie_match(a, b):
    """
    @param a, b: Netflix movie objects
    @return: True if equivalanet movies, False otherwise
    """
    return a["title"]["regular"] == b["title"]["regular"]

def _at_home(netflix, movie):
    """
    @param moive: Netflix movie object (eg, has fields 'id', 'title''short', 'title''regular')
    @return: True if title is at home; False otherwise
    """
    homies = netflix.user.getInfo('at home')
    for home in homies["at_home"]["at_home_item"]:
        if _movie_match(home, movie):
            return True
    return False

def _watched_before(netflix, movie):
    """
    @param movie: Netflix movie object
    @return: True if have watched movie before; False otherwise
    NOTE: if movie is currently at home, will return False
    """
    # detect if movie has been watched before
    start_index = 0
    max_results = 500
    
    done = False
    while not done:
        # get history
        history = netflix.user.getRentalHistory(startIndex=start_index, maxResults=max_results)
        # did we get all results, or will we have to retrieve more
        print
        print "number of results", history["rental_history"]["number_of_results"]
        print "max results + start_index", max_results + start_index
        if int(history["rental_history"]["number_of_results"]) > max_results + start_index:
            start_index = max_results + start_index + 1
            print "new start index", start_index
        else:
            done = True
        
        for k in history["rental_history"]["rental_history_item"]:
            if _movie_match(k, movie):
                return True
    return False

def _find_best_match(netflix, title):
    """
    @param title: string search phrase, eg title of movie
    @return: Netflix movie object that best matches the search term; None otherwise
    """
    matches = NetflixCatalog(netflix).searchTitles(title)
    if not matches:
        return False
    # for now, the first match is the right movie
    return matches[0]

def _log(logfile, message, send_email=False, private=True):
    msg = "%s: %s\n" % (datetime.datetime.now(), message)
    # write to file
    logfile.write(msg)
    
    email_msg = """
-~= %s =~-
%s
\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
y0Uve b33n p4wnd bY #1 F!rs1 in 1!ne
http://github.com/diN0bot/H-cK-teh-P-4N37-N-TF-1X--1/
""" % (datetime.datetime.now(), message)
    email_sbj = "H$cK teh P!4N37!!1"
    # send email if specified
    if send_email:
        from django.core.mail import send_mail
        if private:
            recips = settings.PRIVATE_EMAIL_RECIPIENTS
        else:
            recips = settings.PUBLIC_EMAIL_RECIPIENTS
        send_mail(email_sbj,
                  email_msg,
                  "#1F!rs1in1!ne@H4cKtehP14N37.com",
                  recips,
                  fail_silently=True)
    
def make_number_one(netflix, title, log, watch_again_is_ok=True):
    """
    @param title: string movie title or title search term
    @param watch_again_is_ok: if False, will only add movie to queue
        if not in rental history
    @return: True if title is first in queue at completion of method
        (may have been in queue already at another position or at #1,
        or may have been added to queue)
    """
    # search for movie id for string title
    bestmatch = _find_best_match(netflix, title)
    if not bestmatch:
        _log(log, "match not found for %s" % title, send_email=False, private=True)
        return False
    
    # detect if movie is at home
    at_home = _at_home(netflix, bestmatch)
    if at_home:
        _log(log, "%s is on its way to the B$DH4U5 OMGSQUEEL!!!1" % bestmatch["title"]["regular"], send_email=True, private=False)
        return False
    
    if not watch_again_is_ok:
        # detect if have already watched
        watched_before = _watched_before(netflix, bestmatch)
        if watched_before:
            _log(log, "%s was watched before" % bestmatch["title"]["regular"], send_email=False, private=True)
            return False

    # we're limited to 4 calls a second so...
    time.sleep(1)
    
    # for fun, see if movie is already in queue
    queue = NetflixUserQueue(netflix.user)
    found = False
    for item in queue.getAvailable(maxResults=500)["queue"]["queue_item"]:
        if _movie_match(item, bestmatch):
            found = True
            if item["position"] != "1":
                _log(log, "%s was at position %s" % (bestmatch["title"]["regular"],
                                                     item["position"]),
                                                     send_email=True,
                                                     private=True)
                break
    if not found:
        _log(log, "%s added to queue" % bestmatch["title"]["regular"],
                                        send_email=True,
                                        private=True)
    
    """
    import simplejson
    movie_id = re.findall("http://.*/(\d+)$", bestmatch["id"])
    if movie_id:
        movie_id = movie_id[0]
        #print "BEST MATHC", simplejson.dumps(bestmatch, indent=4)
        print "GET AV T", simplejson.dumps(queue.getAvailableTitle(movie_id), indent=4)
    """
    
    # add title to first place
    queue = NetflixUserQueue( netflix.user )
    queue.addTitle( urls=[bestmatch["id"]], position=1 )
    return True

if __name__ == '__main__':  

    if not settings.USER['request']['key'] or not settings.USER['access']['key'] or not settings.USER['request']['secret'] or not settings.USER['access']['secret']:
        print "Please first run generate_user_keys.py to populate the USER values in settings.py"
        sys.exit(1)

    netflix = NetflixClient(settings.APP_NAME, settings.API_KEY, settings.API_SECRET, settings.CALLBACK)
    netflix.user = NetflixUser(settings.USER, netflix)
    
    LOG = "%s/the_log" % settings.PROJECT_HOME 
    log = open(LOG, 'a')
    
    FILENAME = "%s/movies_i_want_to_watch" % settings.PROJECT_HOME
    f = open(FILENAME, 'r')
    keepers = []
    deed_is_done = False
    for line in f.readlines():
        title = line.strip()
        if not title:
            continue
        if not deed_is_done:
            result = make_number_one(netflix, title, log=log, watch_again_is_ok=True)
            if result:
                deed_is_done = True
            else:
                _log(log, "%s removed from #1 First in Line movie list" % title)
        if deed_is_done:
            keepers.append(title)
    f.close()
    f = open(FILENAME, 'w')
    for keeper in keepers:
        f.write("%s\n" % keeper)
    f.close()
    
    log.close()
