import datetime
import os

import pytz
import requests
from pixivpy3 import PixivAPI, PixivError


# Info needed:
#
# Unique identifier
#
# Author name
# Author handle
# Author avatar
# Profile URL
#
# Source website
#
# Image url(s)
# Image page url
# Image timestamp
# Image dimensions
# Image type (Pixiv only; can be image, manga, or animation)

class Pixiv(object):
    def __init__(self, dbDict, downloadDirectory, avatarDirectory):
        self.dbDict = dbDict
        self.username = self.dbDict.get('pixivUsername')
        self.password = self.dbDict.get('pixivPassword')
        self.downloadDirectory = downloadDirectory
        self.avatarDirectory = avatarDirectory
        os.makedirs(self.downloadDirectory, exist_ok=True)
        os.makedirs(self.avatarDirectory, exist_ok=True)
        self.api = PixivAPI()
        self.authorize()

    def authorize(self):
        self.username = self.dbDict.get('pixivUsername')
        self.password = self.dbDict.get('pixivPassword')
        if self.username and self.password:
            self.api.login(self.username, self.password)


    def loadWorks(self):
        print('Retrieving Pixiv works')
        self.authorize()
        feeds = self.api.me_feeds()
        workIds = [r['ref_work']['id'] for r in feeds['response'] if r['type'] == 'add_illust']
        workDicts = [self._getWorkDict(workId) for workId in workIds]
        works = [w for workDict in workDicts for w in self._getImageData(workDict)]
        return works


    def _getWorkDict(self, workId):
        url = 'https://public-api.secure.pixiv.net/v1/works/' + workId + '.json'
        result = self.api.auth_requests_call('GET', url)
        try:
            return self.api.parse_result(result)
        except PixivError as p:
            return {'status' : 'failure', 'errors' : str(p)}

    def _getImageData(self, workDict):
        imageList = []
        for imageDict in workDict['response']:
            imageData = {
                'identifier'      : '',
                'authorName'      : '',
                'authorHandle'    : '',
                'authorAvatarUrl' : '',
                'profileUrl'      : '',
                'website'         : '',
                'imageTitle'      : '',
                'imageUrls'       : [],
                'imagePageUrl'    : '',
                'imageTimestamp'  : '',
                'imageType'       : '',
                'nsfw'            : False,
                'width'           : '500',
                'height'          : '500',
                'success'         : False,
                'error'           : 'Unknown error',
            }

            if workDict['status'] == 'success':
                identifier = str(imageDict.get('id'))
                if identifier not in self.dbDict['works']: # Skip images we've already loaded
                    user = imageDict.get('user') or {}
                    imageData['identifier']      = identifier
                    imageData['authorName']      = str(user.get('name'))
                    imageData['authorHandle']    = str(user.get('account'))
                    imageData['authorAvatarUrl'] = self._getAvatarUrl(str((user.get('profile_image_urls') or {}).get('px_50x50')))
                    imageData['profileUrl']      = 'http://www.pixiv.net/member.php?id=' + str(user.get('id'))
                    imageData['website']         = 'Pixiv'
                    imageData['imageTitle']      = str(imageDict.get('title'))
                    imageData['imageUrls']       = self._getImageUrls(imageDict)
                    imageData['imagePageUrl']    = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + str(imageDict.get('id'))
                    imageData['imageTimestamp']  = str(max(imageDict.get('created_time'), imageDict.get('reupoloaded_time', '')))
                    imageData['imageType']       = str(imageDict.get('type'))
                    imageData['nsfw']            = str(imageDict.get('age_limit') != 'all-age')
                    imageData['width']           = str(imageDict.get('width')) or '500'
                    imageData['height']          = str(imageDict.get('height')) or '500'
                    imageData['success']         = str(imageDict.get('status') == 'success')
                    imageData['error']           = str(imageDict.get('errors'))

                    self.dbDict['works'][identifier] = imageData
            else:
                raise RuntimeError('Failed Pixiv API call: ' + workDict.get('errors'))

        return imageList

    def _parseTime(self, imageDict):
        s = max(imageDict.get('created_time', ''), imageDict.get('reupoloaded_time', ''))
        return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC).isoformat()

    def _getAvatarUrl(self, remoteUrl):
        return self._downloadImage(remoteUrl, self.avatarDirectory)

    def _getImageUrls(self, imageDict):
        workType = imageDict.get('type')
        if workType == 'illustration':
            urlDict = imageDict.get('image_urls') or {}
            urls = [self._generateImageUrl(urlDict.get('small') or urlDict.get('medium') or urlDict.get('large'))]

        elif workType == 'manga':
            pages = (imageDict.get('metadata') or {}).get('pages') or []
            def getMangaUrl(d):
                urld = d.get('image_urls')
                return self._generateImageUrl(urld.get('small') or urld.get('medium') or urld.get('large'))
            urls = [getMangaUrl(item) for item in pages]

        # Ugoira handling falls through to default for now
        # elif workType == 'ugoira':
        #     pass

        else:
            #Default case; all response types seem to have at least something in image_urls
            urlDict = imageDict.get('image_urls') or {}
            urls = [urlDict.get('small') or urlDict.get('medium') or urlDict.get('large')]

        urls = [self._downloadImage(url, self.downloadDirectory) for url in urls]
        return urls

    def _generateImageUrl(self, url):
        # Construct the URL for the full-res image. Super brittle; entirely dependent on Pixiv never changing anything
        leftSide  = url[:url.find('pixiv.net')+10]
        rightSide = url[url.find('/img/'):].replace('_master1200', '')
        return leftSide + 'img-original' + rightSide


    def _downloadImage(self, url, directory):
        print('Downloading ' + url)
        def attemptDownload(attemptUrl, suffix):
            attemptUrl = '.'.join((attemptUrl.rpartition('.')[0], suffix))
            return requests.get(attemptUrl, headers={'referer': attemptUrl[:attemptUrl.find('/img')]}, stream=True)

        r = attemptDownload(url, 'png')
        if r.status_code == 404:
            r = attemptDownload(url, 'jpg')
            if r.status_code == 404:
                r = attemptDownload(url, 'gif')

        if r.status_code == 200:
            filename = url.split('/')[-1]
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                print ('File already downloaded; skipping')
            else:
                with open(filepath, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
            return '/'.join((directory, filename))
        else:
            return r.status_code + ' ' + url


def main():
    pass


if __name__ == '__main__':
    main()
