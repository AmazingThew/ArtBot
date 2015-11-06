import json
import shelve

from flask import Flask, redirect, send_file, jsonify, request, render_template

from loaders.deviantart import DeviantArt, DeviantArtApiError
from loaders.pixiv import Pixiv


expiredToken = 'b5d4098c2683a7a5e89adf728b424feab3678b84a81c586b0b'

DA_AUTH_REDIRECT = '/deviantartAuthorizationRedirect'

PIXIV_DOWNLOAD_DIRECTORY = 'static/downloaded'

USE_PIXIV      = True
USE_DEVIANTART = True

MAX_WORKS_ON_PAGE = 100


class ArtBot(object):

    def __init__(self, shelf):
        self.app = Flask(__name__, static_folder='static')

        self.shelf = shelf
        self.initShelf()

        if USE_PIXIV: self.pixiv = Pixiv(self.shelf, PIXIV_DOWNLOAD_DIRECTORY)
        if USE_DEVIANTART: self.deviantart = DeviantArt(self.shelf, 'http://localhost:58008'+DA_AUTH_REDIRECT)

        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/getWorks', 'getWorks', self.getWorks)
        self.app.add_url_rule('/getLoginDetails', 'getLoginDetails', self.getLoginDetails)
        self.app.add_url_rule('/submitLoginDetails', 'submitLoginDetails', self.submitLoginDetails, methods=['POST'])
        self.app.add_url_rule('/authorizeDeviantart', 'authorizeDeviantart', self.authorizeDeviantart)
        self.app.add_url_rule(DA_AUTH_REDIRECT, 'deviantartAuthorizationRedirect', self.deviantartAuthorizationRedirect)

        self.app.register_error_handler(DeviantArtApiError, self.handle_invalid_usage)

        self.app.run(debug=True, port=58008)


    def initShelf(self):
        if not self.shelf.get('works'): self.shelf['works'] = {}
        # self.shelf['works'] = {}
        # shelf['deviantartToken'] = 'fart'
        # shelf['deviantartRefreshToken'] = 'also fart'
        # shelf['pixivUsername'] = 'this too is fart'
        # shelf['pixivPassword'] = 'yet further fart'


    def index(self):
        if USE_PIXIV and not (self.shelf.get('pixivUsername') and self.shelf.get('pixivPassword')):
            return redirect('/getLoginDetails')
        return send_file('static/index.html')


    def getLoginDetails(self):
        return send_file('static/loginDetails.html')


    def submitLoginDetails(self):
        self.shelf['pixivUsername'] = request.form['pixivUsername']
        self.shelf['pixivPassword'] = request.form['pixivPassword']
        if USE_PIXIV: self.pixiv.authorize()
        return redirect('/')


    def getWorks(self):
        if USE_DEVIANTART: self.deviantart.loadWorks()
        if USE_PIXIV:      self.pixiv.loadWorks()
        self.shelf.sync()

        works = list(sorted(self.shelf['works'].values(), key=lambda x: x['imageTimestamp'], reverse=True))[:MAX_WORKS_ON_PAGE]
        return json.dumps(works)


    def persistWorks(self):
        pass


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

def main():
    with shelve.open('db', writeback=True) as shelf:
        ArtBot(shelf)


if __name__ == '__main__':
    main()
    # main()