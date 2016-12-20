import json
import os
import pickle
from pprint import pprint

import itertools
from flask import Flask, redirect, send_file, jsonify, request, render_template

from loaders.deviantart import DeviantArt, DeviantArtApiError
from loaders.pixiv import Pixiv
from loaders.artstation import ArtStation


DA_AUTH_REDIRECT = '/deviantartAuthorizationRedirect'

PIXIV_DOWNLOAD_DIRECTORY = 'static/downloaded'
PIXIV_AVATAR_DIRECTORY   = 'static/avatars'

USE_PIXIV      = True
USE_DEVIANTART = True
USE_ARTSTATION = False

MAX_WORKS_ON_PAGE = 150

DB_FILENAME = 'db'


class ArtBot(object):

    def __init__(self):
        self.app = Flask(__name__, static_folder='static')

        self.dbDict = None
        self.initDb()

        if USE_PIXIV: self.pixiv = Pixiv(self.dbDict, PIXIV_DOWNLOAD_DIRECTORY, PIXIV_AVATAR_DIRECTORY)
        if USE_DEVIANTART: self.deviantart = DeviantArt(self.dbDict, 'http://localhost:58008'+DA_AUTH_REDIRECT)
        if USE_ARTSTATION: self.artstation = ArtStation(self.dbDict, '')

        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/getWorks', 'getWorks', self.getWorks)
        self.app.add_url_rule('/getLoginDetails', 'getLoginDetails', self.getLoginDetails)
        self.app.add_url_rule('/submitLoginDetails', 'submitLoginDetails', self.submitLoginDetails, methods=['POST'])
        self.app.add_url_rule('/authorizeDeviantart', 'authorizeDeviantart', self.authorizeDeviantart)
        self.app.add_url_rule(DA_AUTH_REDIRECT, 'deviantartAuthorizationRedirect', self.deviantartAuthorizationRedirect)

        self.app.register_error_handler(DeviantArtApiError, self.handle_invalid_usage)

        self.app.run(debug=True, port=58008)


    def initDb(self):
        if os.path.isfile(DB_FILENAME):
            with open(DB_FILENAME, 'rb') as dbFile:
                try:
                    self.dbDict = pickle.load(dbFile)
                except Exception as e:
                    print('Exception loading db file:')
                    print(e)

        if not isinstance(self.dbDict, dict):
            print('Unable to parse db file, defaulting to empty db')
            self.dbDict = {}

        if not self.dbDict.get('works'): self.dbDict['works'] = {}


    def index(self):
        if USE_PIXIV and not (self.dbDict.get('pixivUsername') and self.dbDict.get('pixivPassword')):
            return redirect('/getLoginDetails')
        return send_file('static/index.html')


    def getLoginDetails(self):
        return send_file('static/loginDetails.html')


    def submitLoginDetails(self):
        self.dbDict['pixivUsername'] = request.form['pixivUsername']
        self.dbDict['pixivPassword'] = request.form['pixivPassword']
        if USE_PIXIV: self.pixiv.authorize()
        return redirect('/')


    def getWorks(self):
        if USE_DEVIANTART: self.deviantart.loadWorks()
        if USE_PIXIV:      self.pixiv.loadWorks()
        if USE_ARTSTATION: self.artstation.loadWorks()

        works = list(sorted(self.dbDict['works'].values(), key=lambda x: x['imageTimestamp'], reverse=True))[:MAX_WORKS_ON_PAGE]

        self.cleanDb(works)
        self.persistDb()
        return json.dumps(works)


    def cleanDb(self, works):
        discard = list(sorted(self.dbDict['works'].items(), key=lambda x: x[1]['imageTimestamp'], reverse=True))[MAX_WORKS_ON_PAGE:]
        [self.dbDict['works'].pop(key) for (key, val) in discard]

        # Clean images
        keepImages = itertools.chain(*(work['imageUrls'] for work in works))
        keepImages = set(os.path.split(url)[1] for url in keepImages if not url.startswith('http'))
        existingImages = set(os.path.split(url)[1] for url in os.listdir(PIXIV_DOWNLOAD_DIRECTORY))
        imagesToRemove = existingImages - keepImages

        [os.remove(os.path.join(PIXIV_DOWNLOAD_DIRECTORY, name)) for name in imagesToRemove]

        # Clean avatars
        keepAvatars = (work['authorAvatarUrl'] for work in works)
        keepAvatars = set(os.path.split(url)[1] for url in keepAvatars if not url.startswith('http'))
        existingAvatars = set(os.path.split(url)[1] for url in os.listdir(PIXIV_AVATAR_DIRECTORY))
        avatarsToRemove = existingAvatars - keepAvatars

        [os.remove(os.path.join(PIXIV_AVATAR_DIRECTORY, name)) for name in avatarsToRemove]


    def persistDb(self):
        print('Persisting to disk')
        with open(DB_FILENAME, 'wb') as dbFile:
            pickle.dump(self.dbDict, dbFile)


    def authorizeDeviantart(self):
        return render_template('authorizeDeviantart.html', url=self.deviantart.getAuthorizationUrl())


    def deviantartAuthorizationRedirect(self):
        self.deviantart.handleAuthorizationCallback(request)
        return redirect('/')


    def handle_invalid_usage(self, error):
        print('ERROR HANDLING')
        print(error.message)
        print(self.deviantart.token)
        response = jsonify(error.message)
        response.status_code = error.status_code
        return response


def wipeWorks():
    with open(DB_FILENAME, 'rb') as dbFile:
        dbDict = pickle.load(dbFile)

    dbDict['works'] = {}

    with open(DB_FILENAME, 'wb') as dbFile:
        pickle.dump(dbDict, dbFile)

if __name__ == '__main__':
    wipeWorks()
    ArtBot()