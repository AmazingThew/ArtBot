import datetime
import os
import itertools
import pytz
import requests
import zipfile
import subprocess
from pixivpy3 import PixivAPI
from pprint import pprint


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
    def __init__(self, dbDict, config):
        self.config = config
        self.dbDict = dbDict
        self.username = config['PIXIV_USERNAME']
        self.password = config['PIXIV_PASSWORD']
        self.imageDirectory  = os.path.join(config['PIXIV_DOWNLOAD_DIRECTORY'], 'images')
        self.ugoiraDirectory = os.path.join(config['PIXIV_DOWNLOAD_DIRECTORY'], 'ugoira')
        self.avatarDirectory = os.path.join(config['PIXIV_DOWNLOAD_DIRECTORY'], 'avatars')
        os.makedirs(self.imageDirectory, exist_ok=True)
        os.makedirs(self.ugoiraDirectory, exist_ok=True)
        os.makedirs(self.avatarDirectory, exist_ok=True)
        self.api = PixivAPI()
        self.authorize()

    def authorize(self):
        self.api.login(self.username, self.password)


    def loadWorks(self):
        print('Retrieving Pixiv works')
        self.authorize()
        apiWorks = self.api.me_following_works(1, self.config['MAX_WORKS_ON_PAGE'])
        workDicts = apiWorks['response']
        workDicts = [w for w in workDicts]
        [self._getImageData(workDict) for workDict in workDicts]


    def loadExtraWorkInfo(self):
        updates = []
        worksToUpdate = [work for work in self.dbDict['works'].values() if work['website'] == 'Pixiv' and not work.get('imageUrls')]
        for work in worksToUpdate:
            imageDict = work['pixivMeta']
            extraInfo = {
                'authorAvatarUrl' : self._getAvatarUrl(str(imageDict.get('user').get('profile_image_urls').get('px_50x50'))),
                'imageUrls' : self._getImageUrls(imageDict),
                'pixivMeta' : '',
            }
            updates.append((work['identifier'], extraInfo))

        [self.dbDict['works'][identifier].update(extraInfo) for (identifier, extraInfo) in updates]


    def _getImageData(self, imageDict):
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
            'pixivMeta'       : '',
        }

        identifier = str(imageDict.get('id'))
        if identifier not in self.dbDict['works']: # Skip images we've already loaded
            user = imageDict.get('user') or {}
            imageData['identifier']      = identifier
            imageData['authorName']      = str(user.get('name'))
            imageData['authorHandle']    = str(user.get('account'))
            imageData['authorAvatarUrl'] = None
            imageData['profileUrl']      = 'http://www.pixiv.net/member.php?id=' + str(user.get('id'))
            imageData['website']         = 'Pixiv'
            imageData['imageTitle']      = str(imageDict.get('title'))
            imageData['imageUrls']       = None
            imageData['imagePageUrl']    = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + str(imageDict.get('id'))
            imageData['imageTimestamp']  = str(max(imageDict.get('created_time'), imageDict.get('reupoloaded_time', '')))
            imageData['imageType']       = str(imageDict.get('type'))
            imageData['nsfw']            = str(imageDict.get('age_limit') != 'all-age')
            imageData['width']           = str(imageDict.get('width')) or '500'
            imageData['height']          = str(imageDict.get('height')) or '500'
            imageData['success']         = str(imageDict.get('status') == 'success')
            imageData['error']           = str(imageDict.get('errors'))
            imageData['pixivMeta']       = imageDict #stores the pixiv API info to facilitate late download of images

            self.dbDict['works'][identifier] = imageData


    def _parseTime(self, imageDict):
        s = max(imageDict.get('created_time', ''), imageDict.get('reupoloaded_time', ''))
        return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC).isoformat()

    def _getAvatarUrl(self, remoteUrl):
        return self._downloadImage(remoteUrl, self.avatarDirectory)

    def _getImageUrls(self, imageDict):
        workType = imageDict.get('type')

        if imageDict.get('is_manga') == True or workType == 'manga':
            response = self.api.works(imageDict['id'])
            response = response.get('response')[0] or {}
            metadata = response.get('metadata') or {}
            pages = metadata.get('pages') or []

            def getMangaUrl(d):
                urld = d.get('image_urls')
                return self._generateImageUrl(urld.get('small') or urld.get('medium') or urld.get('large'))

            urls = [getMangaUrl(item) for item in pages]

        elif workType == 'illustration':
            urlDict = imageDict.get('image_urls') or {}
            urls = [self._generateImageUrl(urlDict.get('small') or urlDict.get('medium') or urlDict.get('large'))]

        elif workType == 'ugoira':
            return self._constructUgoira(imageDict.get('id'))

        else:
            #Default case; all response types seem to have at least something in image_urls
            urlDict = imageDict.get('image_urls') or {}
            urls = [urlDict.get('small') or urlDict.get('medium') or urlDict.get('large')]

        urls = [self._downloadImage(url, self.imageDirectory) for url in urls]
        return urls


    def _generateImageUrl(self, url):
        # Construct the URL for the full-res image. Super brittle; entirely dependent on Pixiv never changing anything
        leftSide  = url[:url.find('pixiv.net')+10]
        rightSide = url[url.find('/img/'):].replace('_master1200', '')
        return leftSide + 'img-original' + rightSide


    def _downloadImage(self, url, directory):
        name = url[url.rfind('/') + 1:url.rfind('.')]
        extant = {name.split('.')[0] : os.path.join(directory, name) for name in os.listdir(directory)}
        if extant.get(name):
            print('Already downloaded {}'.format(url))
            return extant.get(name)


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
            with open(filepath, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
            return '/'.join((directory, filename))
        else:
            return r.status_code + ' ' + url


    def _constructUgoira(self, identifier):
        directory = os.path.join(self.ugoiraDirectory, str(identifier))
        os.makedirs(directory, exist_ok=True)

        response = self.api.works(identifier)
        response = response.get('response')[0] or {}
        metadata = response.get('metadata') or {}
        frameTimes = ['duration {}'.format(delay['delay_msec']/1000) for delay in metadata.get('frames')]
        zipUrl = sorted(metadata['zip_urls'].items())[-1][1]  # I don't think zip_urls will ever be longer than 1 but ??

        zipPath = self._downloadUgoiraZip(zipUrl, directory)
        with zipfile.ZipFile(zipPath, 'r') as zap:
            zap.extractall(directory)

        imagePaths = ["file '{}'".format(fileName) for fileName in os.listdir(directory) if not fileName.endswith('.zip')]
        frameData = '\n'.join(itertools.chain(*zip(imagePaths, frameTimes)))

        concatFile = os.path.join(directory, 'concat.txt')
        print('Writing frame data to: {}'.format(concatFile))
        with open(concatFile, 'w') as f:
            f.write(frameData)

        concatFile = os.path.abspath(os.path.join(os.getcwd(), concatFile))
        workingDirectory = os.path.abspath(os.path.join(os.getcwd(), directory))
        outFile = os.path.join(directory, '{}.webm'.format(identifier))
        ffmpeg = 'ffmpeg -n -f concat -i {} -c:v libvpx -crf 10 -b:v 2M {}.webm'.format(concatFile, identifier)
        print('Rendering video to {}'.format(outFile))
        subprocess.run(ffmpeg, shell=True, cwd=workingDirectory)
        print('Finished rendering')

        return [outFile]


    def _downloadUgoiraZip(self, url, directory):
        print('Downloading ugoira zip: {}'.format(url))
        path = os.path.join(directory, url.split('/')[-1])
        if os.path.exists(path):
            print('Zip already downloaded; skipping')
        else:
            r = requests.get(url, headers={'referer': url[:url.find('/img')]}, stream=True)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

        return path


def main():
    pass


if __name__ == '__main__':
    main()
