import pytz
import requests
import requests.auth
from uuid import uuid4
from urllib.parse import urlencode
from dateutil import parser

class DeviantArtApiError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code



class DeviantArt(object):
    def __init__(self, dbDict, authorizationRedirectUri):
        self.clientId     = '3823'
        self.clientSecret = 'ebdbe992445cd52b086030439f710fb3'
        self.authorizationRedirectUri = authorizationRedirectUri
        self.dbDict = dbDict
        self.token = self.dbDict.get('deviantartToken')
        self.refreshToken = self.dbDict.get('deviantartRefreshToken')


    def getAuthorizationUrl(self):
        params = {
            'response_type' : 'code',
            'client_id'     : self.clientId,
            'redirect_uri'  : self.authorizationRedirectUri,
            'scope'         : 'feed',
            'state'         : str(uuid4()),
        }
        return "https://www.deviantart.com/oauth2/authorize?" + urlencode(params)


    def handleAuthorizationCallback(self, request):
        error = request.args.get('error', '')
        if error:
            return "Error: " + error
        code = request.args.get('code')
        self.getToken(code)


    def getToken(self, code):
        client_auth = requests.auth.HTTPBasicAuth(self.clientId, self.clientSecret)
        post_data = {"grant_type": "authorization_code",
                     "code": code,
                     "redirect_uri": self.authorizationRedirectUri}
        response = requests.post("https://www.deviantart.com/oauth2/token",
                                 auth=client_auth,
                                 data=post_data)
        token_json = response.json()
        token = token_json["access_token"]
        refreshToken = token_json['refresh_token']

        self.token = token
        self.refreshToken = refreshToken
        self.dbDict['deviantartToken'] = token
        self.dbDict['deviantartRefreshToken'] = token


    def refreshAuthorization(self):
        print('Attempting DA auth refresh')
        client_auth = requests.auth.HTTPBasicAuth(self.clientId, self.clientSecret)
        post_data = {"grant_type": "refresh_token",
                     "refresh_token": self.refreshToken}
        response = requests.post("https://www.deviantart.com/oauth2/token",
                                 auth=client_auth,
                                 data=post_data)

        if response.status_code == 200:
            token_json = response.json()
            token = token_json["access_token"]
            refreshToken = token_json['refresh_token']

            self.token = token
            self.refreshToken = refreshToken
            self.dbDict['deviantartToken'] = token
            self.dbDict['deviantartRefreshToken'] = refreshToken


    def loadWorks(self):
        print('Retrieving DeviantArt works')
        self.refreshAuthorization()
        response = requests.get('https://www.deviantart.com/api/v1/oauth2/feed/home?' + urlencode({'access_token' : self.token}))
        if response.status_code != 200:
            print('ERROR')
            print(response.status_code)
            raise DeviantArtApiError(response.json(), status_code=response.status_code)

        return self.parseFeed(response.json())


    def parseFeed(self, responseDict):
        chunks = [(deviation, item['ts']) for item in responseDict['items'] if item['type'] == 'deviation_submitted' for deviation in item['deviations']]

        imageList = []
        for deviation, timestamp in chunks:
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

            userInfo  = deviation.get('author') or {}
            imageInfo = deviation.get('content') or {}
            imageData['identifier']      = deviation.get('deviationid')
            imageData['authorName']      = str(userInfo.get('username'))
            imageData['authorHandle']    = str(userInfo.get('username'))
            imageData['authorAvatarUrl'] = str(userInfo.get('usericon'))
            imageData['profileUrl']      = 'http://' + str(userInfo.get('username')) + '.deviantart.com'
            imageData['website']         = 'DeviantArt'
            imageData['imageTitle']      = str(deviation.get('title'))
            imageData['imageUrls']       = [str(imageInfo.get('src'))]
            imageData['imagePageUrl']    = str(deviation.get('url'))
            imageData['imageTimestamp']  = parser.parse(timestamp).astimezone(pytz.utc).isoformat()
            imageData['imageType']       = '"deviation"'
            imageData['nsfw']            = str(deviation.get('is_mature'))
            imageData['width']           = str(imageInfo.get('width')) or '500'
            imageData['height']          = str(imageInfo.get('height')) or '500'
            imageData['success']         = 'True'
            imageData['error']           = ''

            imageList.append(imageData)

        for d in imageList:
            d['identifier'] = d['identifier'] if isinstance(d['identifier'], str) else d['identifier'][0] #??????????????????????             WHY

            # Just clobber existing data here;
            # DA pulls everything down in one API call so there's no performance to be gained by skipping existing IDs:
            self.dbDict['works'][d['identifier']] = d


def main():
    pass


if __name__ == '__main__':
    main()
