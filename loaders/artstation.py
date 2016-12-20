import itertools
import requests
import requests.auth
import feedparser
from pprint import pprint

import time
from dateutil import parser
from bs4 import BeautifulSoup


class ArtStation(object):
    def __init__(self, dbDict, accountName):
        self.dbDict = dbDict
        self.accountName = accountName


    def loadWorks(self):
        print('Retrieving ArtStation works')
        response = requests.get('https://www.artstation.com/users/{}/following.json'.format(self.accountName))
        if response.status_code == 200:
            json = response.json()
            follows = [(artist['username'], artist['full_name'], artist['large_avatar_url']) for artist in json['data']]
            works = [self._getArtistWorks(*artist) for artist in follows[:1]] #List of lists of works by artist
            for work in itertools.chain(*works):
                self.dbDict['works'][work['identifier']] = work
        else:
            print('Failed to load ArtStation following list: ' + str(response.status_code))



    def _getArtistWorks(self, username, fullName, avatarUrl):
        print('Getting works for artist: ' + username)
        profileUrl = 'https://www.artstation.com/artist/'+username
        feed = feedparser.parse(profileUrl+'.rss')
        if feed['bozo'] != 0:
            print('Failed to load ArtStation artist: ' + username)
            pprint(feed)
            return {}

        constants = {
            'authorName'      : fullName,
            'authorHandle'    : username,
            'authorAvatarUrl' : avatarUrl,
            'profileUrl'      : profileUrl,
        }

        return [self._parse(entry, constants) for entry in feed['entries']]


    def _parse(self, entry, constants):
        title = entry['title']
        title = title[:title.rindex(' by {}'.format(constants['authorName']))]

        soup = BeautifulSoup(entry['content'][0]['value'], 'html.parser')
        imageUrls = [img.get('src') for img in soup.find_all('img')]

        work = {
            'identifier'      : entry['link'],
            'website'         : 'ArtStation',
            'imageTitle'      : title,
            'imageUrls'       : imageUrls,
            'imagePageUrl'    : entry['link'],
            'imageTimestamp'  : time.strftime('%Y-%m-%dT%H:%M:%SZ', entry['published_parsed']),
            'imageType'       : 'art',
            'nsfw'            : False,
            'width'           : '1',
            'height'          : '1',
            'success'         : True,
            'error'           : '',
        }

        work.update(constants)

        return work


def main():
    art = ArtStation({})
    art.loadWorks()


if __name__ == '__main__':
    main()
