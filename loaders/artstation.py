import itertools
import requests
import requests.auth
import feedparser
from pprint import pprint
import time
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
            works = [self._getArtistWorks(*artist) for artist in follows] #List of lists of works by artist
            for work in itertools.chain(*works):
                if work['identifier'] not in self.dbDict['works'].keys():
                    self.dbDict['works'][work['identifier']] = work
        else:
            print('Failed to load ArtStation following list: ' + str(response.status_code))


    def loadExtraWorkInfo(self):
        worksToUpdate = [work for work in self.dbDict['works'].values() if work['website'] == 'ArtStation' and not (work.get('width') or work.get('height')) and len(work['imageUrls']) == 1]

        updates = []
        for work in worksToUpdate:
            title = work['imageTitle']
            urlTitle = work['imagePageUrl'].split('/')[-1]
            print('Loading extra info for work: {}, urlTitle: {}'.format(title, urlTitle))
            response = requests.get('https://www.artstation.com/projects/{}.json'.format(urlTitle))
            if response.status_code == 200:
                json = response.json()

                width = 100
                height = 100
                for asset in json['assets']:
                    if asset.get('image_url') == work['imageUrls'][0]:
                        width = asset['width']
                        height = asset['height']
                        break

                extraInfo = {
                    'nsfw'   : json['adult_content'] or json['admin_adult_content'],
                    'width'  : width,
                    'height' : height,
                }

                updates.append((work['identifier'], extraInfo))
            else:
                print('Failed to retrieve extra info for work: {} (urlTitle: {} ): {}'.format(title, urlTitle, str(response.status_code)))

        [self.dbDict['works'][identifier].update(extraInfo) for (identifier, extraInfo) in updates]


    def _getArtistWorks(self, username, fullName, avatarUrl):
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
            'success'         : True,
            'error'           : '',
        }

        work.update(constants)

        return work


def main():
    pass

if __name__ == '__main__':
    main()
