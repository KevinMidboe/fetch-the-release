import requests
from redis import Redis

import pickle
from urllib.parse import urljoin, quote 
import os
import sys
from pprint import pprint

from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

BASE_URL = os.getenv('BASE_URL') or None
AUTHORIZATION_TOKEN = os.getenv('AUTHORIZATION_TOKEN') or None
CACHE = Redis(host='localhost', port=6379, db=0)


USER = os.getenv('USER') or None
PASS = os.getenv('PASS') or None 

if None in [BASE_URL, USER, PASS]:
    print('ERROR! Set environment variables, see ./.env-example or README')
    exit(0)

# - - Cache

def writeObjectToCache(key, obj):
    print('saving response with key:', key)
    pickledObj = pickle.dumps(obj)
    CACHE.set(key, pickledObj, ex=600)

def readCache(key):
    value = CACHE.get(key)
    if value is None:
        return None
    return pickle.loads(value)

def flushCache():
    CACHE.flushdb(0)

def releaseFromCache(request):
    return False


# - - MISC

METRIC_PREFIX_VALUES = {'KB': 1000, 'MB': 1000000, 'GB': 1000000000} 
def humanReadableToBytes(sizeString):
    [value, prefix] = sizeString.split()
    byteSize = float(value) * METRIC_PREFIX_VALUES[prefix]
    return byteSize


# - - HTTP API

# TODO Move authentication to happen at begining and use the set value throughtout
# could recheck if a request returns un-authed. 
# Releases should therefor not 
def authenticateSeasoned(username, password):
    global AUTHORIZATION_TOKEN
    uri = urljoin(BASE_URL, '/api/v1/user/login')
    payload = { 'username': username, 'password': password }
    print('VERBOSE | Signing in to page: {}'.format(uri))
    response = requests.post(uri, data=payload)
    data = response.json()
    if response.status_code == requests.codes.ok:
        AUTHORIZATION_TOKEN = data['token']
    else:
        print('ERROR! {}: {}'.format(response.status_code, data['error']))
        exit(0) 
    
def fetchRequests(page=1):
    uri = urljoin(BASE_URL, '/api/v2/request?page=' + str(page))
    r = requests.get(uri)
    return r.json()

def releasesFromRequest(request):
    uri = urljoin(BASE_URL, '/api/v1/pirate/search?query=' + quote(request['title']))
    cacheHit = readCache(uri)
    if cacheHit:
        return cacheHit
    headers = { 'authorization': AUTHORIZATION_TOKEN }

    print('VERBOSE | Searcing for releases at {} with auth token: {}'.format(uri, AUTHORIZATION_TOKEN))
    r = requests.get(uri, headers=headers)
    
    if r.status_code == requests.codes.unauthorized:
        print('uathed. Signing in as {}'.format(USER))
        authenticateSeasoned(USER, PASS)
        releasesFromRequest(request)
        return
    
    elif r.status_code == requests.codes.ok:
        response = r.json()
        writeObjectToCache(uri, response)
        return response

    else:
        return None


# - - FORMATTING

def printReleases(releases):
    if len(releases) == 0:
        print('No releases found')
        return None

    releases.sort(key=lambda x: humanReadableToBytes(x['size']), reverse=True)
    for release in releases:
        print('{:80} | {}\t | {}'.format(release['name'], release['size'], release['seed']))


allReleases = []
def takePageGetRequestsAndReleases(page=1):
    global allReleases
    requests = fetchRequests(page)
    results = requests['results']
    totalPages = requests['total_pages']

    for request in results:
        print('Finding torrent for:', request['title'])
        releases = releasesFromRequest(request)
        if releases:
            printReleases(releases['results'])
            allReleases.append({'req': request, 'rel': releases})

    if totalPages - page > 0:
        print('More pages to index, moving to page:', page + 1)
        takePageGetRequestsAndReleases(page + 1)
    return allReleases

def main():
    print('Fetching all requested movies and shows..')
    TwentyOneForever = takePageGetRequestsAndReleases()
    exit(0)

    
    requests = fetchRequests() 
    results = requests['results']
    currentPage = requests['page']
    totalPages = requests['total_pages']

    mediaWithReleases = []

    for result in results:
        print('Finding torrents for:', result['title'])
        releases = releasesFromRequest(result)
        if releases:
            printReleases(releases['results'])


        mediaWithReleases.append({'rel': releases, 'media': result})

#   pprint(mediaWithReleases[:5])
       
    print(type(totalPages))
    print(type(currentPage))
    pagesLeft = totalPages - currentPage 
    print('pages left:', pagesLeft)



if __name__ == '__main__':
    main()
