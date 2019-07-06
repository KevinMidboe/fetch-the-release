import requests
from redis import Redis

import pickle
from urllib.parse import urljoin, quote 
import os
from pprint import pprint

BASE_URL = 'https://api.kevinmidboe.com/'
AUTHORIZATION_TOKEN = None 
CACHE_FILE = './cache.pickle'
CACHE = Redis(host='localhost', port=6379, db=0)

def writeObjectToCache(key, obj):
    print('object to cache', obj)
    pickledObj = pickle.dumps(obj)
    CACHE.set(key, pickledObj)

def readCache(key):
    value = CACHE.get(key)
    return pickle.loads(value)

def flushCache():
    CACHE.flushdb(0)

def releaseFromCache(request):
    return False

def authenticateSeasoned(username, password):
    global AUTHORIZATION_TOKEN
    uri = urljoin(BASE_URL, '/api/v1/user/login')
    payload = { 'username': username, 'password': password }
    r = requests.post(uri, data=payload)
    data = r.json()
    AUTHORIZATION_TOKEN = data['token']

def fetchRequests(pages=1):
    uri = urljoin(BASE_URL, '/api/v2/request')
    r = requests.get(uri)
    return r.json()

def releasesFromRequest(request):
    uri = urljoin(BASE_URL, '/api/v1/pirate/search?query=' + quote(request['title']))
    cacheHit = readCache(uri)
    if cacheHit:
        return cacheHit
    headers = { 'authorization': AUTHORIZATION_TOKEN }

    r = requests.get(uri, headers=headers)
    
    if r.status_code == requests.codes.unauthorized:
        print('uath')
        authenticateSeasoned('kevin', 'test123')
        releasesFromRequest(request)
        return
    
    elif r.status_code == requests.codes.ok:
        response = r.json()
        writeObjectToCache(uri, response)
        return response

    else:
        return None
        

def main():
    requests = fetchRequests() 
    results = requests['results']
    totalPages = requests['total_pages']

    mediaWithReleases = []

    for result in results:
        releases = releasesFromRequest(result)
        mediaWithReleases.append({'rel': releases, 'media': result})
    pprint(mediaWithReleases[:3])

    for l in mediaWithReleases[:3]:
        if len(l['rel']['results']) > 0:
            print(l['rel']['results'][0]['release_type'])
        
    print(totalPages)



if __name__ == '__main__':
    main()
