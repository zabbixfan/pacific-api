import urllib2,json,urllib
from hashlib import sha1
from hmac import new as hmac
def searchRequest(url,message,privatekey):
    sig = hmac(privatekey, message, sha1).hexdigest()
    url = '{}/?sig={}&{}'.format(url,urllib.quote_plus(sig), message)
    data = urllib2.urlopen(url)
    data = json.loads(data.read())
    return data