import json
import os
import pickle
from pprint import pprint
import itertools
import sys
import shutil
from flask import Flask, redirect, send_file, jsonify, request, render_template
from loaders.deviantart import DeviantArt, DeviantArtApiError
from loaders.pixiv import Pixiv
from loaders.artstation import ArtStation


DA_AUTH_REDIRECT = '/deviantartAuthorizationRedirect'
DB_FILENAME = 'db'

class ArtBot(object):

    def __init__(self):
        try:
            with open('config.json', 'r') as configFile:
                self.config = json.load(configFile)
        except Exception as e:
            print('Unable to read config.json!')
            print(e)
            sys.exit(-1)

        self.app = Flask(__name__, static_folder='static')

        self.dbDict = None
        self.initDb()

        if self.config['USE_PIXIV']: self.pixiv = Pixiv(self.dbDict, self.config)
        if self.config['USE_DEVIANTART']: self.deviantart = DeviantArt(self.dbDict, 'http://localhost:{}{}'.format(self.config['PORT'], DA_AUTH_REDIRECT))
        if self.config['USE_ARTSTATION']: self.artstation = ArtStation(self.dbDict, self.config['ARTSTATION_USERNAME'])

        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/getWorks', 'getWorks', self.getWorks)
        self.app.add_url_rule('/authorizeDeviantart', 'authorizeDeviantart', self.authorizeDeviantart)
        self.app.add_url_rule(DA_AUTH_REDIRECT, 'deviantartAuthorizationRedirect', self.deviantartAuthorizationRedirect)

        self.app.register_error_handler(DeviantArtApiError, self.handle_invalid_usage)

        self.app.run(debug=True, port=self.config['PORT'])


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
        return send_file('static/index.html')


    def getWorks(self):
        if self.config['USE_DEVIANTART']: self.deviantart.loadWorks()
        if self.config['USE_PIXIV']:      self.pixiv.loadWorks()
        if self.config['USE_ARTSTATION']: self.artstation.loadWorks()

        works = list(sorted(self.dbDict['works'].values(), key=lambda x: x['imageTimestamp'], reverse=True))[:self.config['MAX_WORKS_ON_PAGE']]

        self.cleanDb(works)
        self.loadExtraWorkInfo()
        self.persistDb()
        return json.dumps(works)


    def loadExtraWorkInfo(self):
        if self.config['USE_ARTSTATION']: self.artstation.loadExtraWorkInfo()


    def cleanDb(self, works):
        discard = list(sorted(self.dbDict['works'].items(), key=lambda x: x[1]['imageTimestamp'], reverse=True))[self.config['MAX_WORKS_ON_PAGE']:]
        [self.dbDict['works'].pop(key) for (key, val) in discard]

        # Clean images
        keepImages = itertools.chain(*(work['imageUrls'] for work in works))
        keepImages = set(os.path.split(url)[1] for url in keepImages if not url.startswith('http'))
        existingImages = set(os.path.split(url)[1] for url in os.listdir(self.pixiv.imageDirectory))
        imagesToRemove = existingImages - keepImages

        [os.remove(os.path.join(self.pixiv.imageDirectory, name)) for name in imagesToRemove]

        # Clean avatars
        keepAvatars = (work['authorAvatarUrl'] for work in works)
        keepAvatars = set(os.path.split(url)[1] for url in keepAvatars if not url.startswith('http'))
        existingAvatars = set(os.path.split(url)[1] for url in os.listdir(self.pixiv.avatarDirectory))
        avatarsToRemove = existingAvatars - keepAvatars

        [os.remove(os.path.join(self.pixiv.avatarDirectory, name)) for name in avatarsToRemove]

        # Clean videos
        allIds = (work['identifier'] for work in works)
        videoIds = next(os.walk(self.pixiv.ugoiraDirectory))[1]
        videoDirsToRemove = set(videoIds) - set(allIds)

        [shutil.rmtree(os.path.join(self.pixiv.ugoiraDirectory, directory)) for directory in videoDirsToRemove]


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

def viewDb():
    with open(DB_FILENAME, 'rb') as dbFile:
        dbDict = pickle.load(dbFile)
        pprint(dbDict)

if __name__ == '__main__':
    # wipeWorks()
    # viewDb()
    ArtBot()