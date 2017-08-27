import requests
import requests.auth
import dateutil.parser
import pytz
from bs4 import BeautifulSoup


class ArtStation(object):
    def __init__(self, dbDict, config):
        self.config = config
        self.dbDict = dbDict
        self.authorize()

    def authorize(self):
        self.session = requests.Session()
        loginUrl = 'https://www.artstation.com/users/sign_in'
        page = self.session.get(loginUrl)
        soup = BeautifulSoup(page.text, 'html.parser')
        csrf = soup.find('input', {'name': 'authenticity_token'})['value']

        inputs = {
            'utf8': '✓',
            'authenticity_token': csrf,
            'user_return_to': '',
            'user[email]': self.config['ARTSTATION_EMAIL'],
            'user[password]': self.config['ARTSTATION_PASSWORD'],
            'user[remember_me]': 'true',
            'button': '',
        }

        self.session.post(loginUrl, data=inputs)

    def loadWorks(self):
        print('Retrieving ArtStation works')
        response = self.session.get('https://www.artstation.com/projects.json?page=1&sorting=following')
        if response.status_code == 200:
            worksJson = response.json()['data']

            if len(worksJson) == 0:
                print('WARNING: ArtStation API indicates no works; login info is most likely incorrect!')

            works = [self._parseWork(workJson) for workJson in worksJson]

            for work in works:
                if work['identifier'] not in self.dbDict['works'].keys():
                    self.dbDict['works'][work['identifier']] = work
        else:
            print('Failed to load ArtStation works: ' + str(response.status_code))

    def _parseWork(self, workJson):
        return {
            'identifier'     : str(workJson['id']),
            'authorName'     : workJson['user']['full_name'],
            'authorHandle'   : workJson['user']['username'],
            'authorAvatarUrl': workJson['user']['large_avatar_url'],
            'profileUrl'     : workJson['user']['permalink'],
            'website'        : 'ArtStation',
            'imageTitle'     : workJson['title'],
            'imageUrls'      : [],
            'imagePageUrl'   : workJson['permalink'],
            'imageTimestamp' : dateutil.parser.parse(workJson['published_at']).astimezone(pytz.utc).isoformat(),
            'imageType'      : 'art',
            'nsfw'           : workJson['adult_content'] or workJson['admin_adult_content'],
            'width'          : None,
            'height'         : None,
            'success'        : False,
            'error'          : '',
            'pixivMeta'      : '',
        }

    def loadExtraWorkInfo(self):
        worksToUpdate = [work for work in self.dbDict['works'].values() if
                         work['website'] == 'ArtStation' and not (work.get('width') or work.get('height')) and not work['imageUrls']]

        if worksToUpdate: print("Found {} new ArtStation works".format(len(worksToUpdate)))

        updates = []
        for work in worksToUpdate:
            title = work['imageTitle']
            urlTitle = work['imagePageUrl'].split('/')[-1]
            response = self.session.get('https://www.artstation.com/projects/{}.json'.format(urlTitle))
            if response.status_code == 200:
                assets = response.json()['assets']
                extraInfo = {
                    'imageUrls' : [asset['image_url'] for asset in assets],
                    'width'     : str(assets[0]['width']),
                    'height'    : str(assets[0]['height']),
                    'success'   : 'True',
                }
                updates.append((work['identifier'], extraInfo))
            else:
                print('Failed to retrieve extra info for work: {} (urlTitle: {} ): {}'.format(title, urlTitle, str(
                    response.status_code)))

        [self.dbDict['works'][identifier].update(extraInfo) for (identifier, extraInfo) in updates]

def main():
    pass

if __name__ == '__main__':
    main()
